
// compile:
// c++ -lavutil -lavformat -lavcodec ffmpeg-seek-bug.cpp

#define __STDC_LIMIT_MACROS // INT64_MIN and co
#include <stdio.h>
#include <stdint.h>
#include <assert.h>
#include <string>

extern "C" {
#include <libavformat/avformat.h>
#include <libswresample/swresample.h>
}

static FILE* songFile;


static int player_read_packet(void*, uint8_t* buf, int buf_size) {
	//printf("read: size:%i\n", buf_size);
	return fread(buf, 1, buf_size, songFile);
}

static int64_t player_seek(void*, int64_t offset, int whence) {
	//printf("seek: offset:%lli whence:%i\n", offset, whence);

	if(whence == AVSEEK_SIZE) return -1; // Ignore and return -1. This is supported by FFmpeg.
	if(whence & AVSEEK_FORCE) whence &= ~AVSEEK_FORCE; // Can be ignored.
	if(whence != SEEK_SET && whence != SEEK_CUR && whence != SEEK_END) {
		printf("player_seek: invalid whence in params offset:%lli whence:%i\n", offset, whence);
		return -1;
	}
	if(whence == SEEK_SET && offset < 0) {
		// This is a bug in FFmpeg: https://trac.ffmpeg.org/ticket/4038
		abort();
		return -1;
	}
	
	int ret = fseeko(songFile, offset, whence);
	if(ret < 0) {
		printf("player_seek() error: %s\n", strerror(errno));
		return -1;
	}
	
	return ftello(songFile);
}

static
AVIOContext* initIoCtx() {
	int buffer_size = 1024 * 4;
	unsigned char* buffer = (unsigned char*)av_malloc(buffer_size);
	
	AVIOContext* io = avio_alloc_context(
										 buffer,
										 buffer_size,
										 0, // writeflag
										 0, // opaque
										 player_read_packet,
										 NULL, // write_packet
										 player_seek
										 );
	
	return io;
}

static
AVFormatContext* initFormatCtx() {
	AVFormatContext* fmt = avformat_alloc_context();
	if(!fmt) return NULL;
	
	fmt->pb = initIoCtx();
	if(!fmt->pb) {
		printf("initIoCtx failed\n");
	}
	
	fmt->flags |= AVFMT_FLAG_CUSTOM_IO;
	
	return fmt;
}

static void closeInputStream(AVFormatContext* formatCtx) {
	if(formatCtx->pb) {
		if(formatCtx->pb->buffer) {
			av_free(formatCtx->pb->buffer);
			formatCtx->pb->buffer = NULL;
		}
		// avformat_close_input freeing this indirectly? I got a crash here in avio_close
		//av_free(formatCtx->pb);
		//formatCtx->pb = NULL;
	}
	for(int i = 0; i < formatCtx->nb_streams; ++i) {
		avcodec_close(formatCtx->streams[i]->codec);
	}
	avformat_close_input(&formatCtx);
}

static int songAudioStreamIdx;
static AVStream* songAudioStream;

/* open a given stream. Return 0 if OK */
static int stream_component_open(AVFormatContext* ic, int stream_index)
{
	AVCodecContext *avctx;
	AVCodec *codec;
	
	if(stream_index < 0 || stream_index >= ic->nb_streams)
		return -1;
	avctx = ic->streams[stream_index]->codec;
	
	codec = avcodec_find_decoder(avctx->codec_id);
	if(!codec) {
		printf("avcodec_find_decoder failed (%s)\n", ic->iformat->name);
		return -1;
	}
	
	if(avctx->lowres > codec->max_lowres) {
		av_log(avctx, AV_LOG_WARNING, "The maximum value for lowres supported by the decoder is %d\n",
			   codec->max_lowres);
		avctx->lowres= codec->max_lowres;
	}
	
	if(avctx->lowres) avctx->flags |= CODEC_FLAG_EMU_EDGE;
	if(codec->capabilities & CODEC_CAP_DR1)
		avctx->flags |= CODEC_FLAG_EMU_EDGE;
	
	if (avcodec_open2(avctx, codec, NULL /*opts*/) < 0) {
		printf("avcodec_open2 failed (%s) (%s)\n", ic->iformat->name, codec->name);
		return -1;
	}
	
	ic->streams[stream_index]->discard = AVDISCARD_DEFAULT;
	switch (avctx->codec_type) {
		case AVMEDIA_TYPE_AUDIO:
			songAudioStreamIdx = stream_index;
			songAudioStream = ic->streams[stream_index];
			
			//player_resetStreamPackets(is);
			break;
		default:
			printf("stream_component_open: not an audio stream\n");
			return -1;
	}
	
	return 0;
}

static AVFormatContext* songCtx;
static double songLen;

static bool openSong(const std::string& filename) {
	
	songFile = fopen(filename.c_str(), "rb");
	if(!songFile) {
		printf("could not open file\n");
		return false;
	}
	
	AVFormatContext* formatCtx = NULL;
	
	const char* fileExt = NULL;
	{
		size_t f = filename.rfind('.');
		if(f != std::string::npos)
			fileExt = &filename[f+1];
	}
	
	AVInputFormat* fmts[] = {
		fileExt ? av_find_input_format(fileExt) : NULL,
		NULL,
		av_find_input_format("mp3")
	};
	for(size_t i = 0; i < sizeof(fmts)/sizeof(fmts[0]); ++i) {
		if(i == 1 && fmts[0] == NULL) continue; // we already tried NULL
		AVInputFormat* fmt = fmts[i];
		
		if(formatCtx)
			closeInputStream(formatCtx);
		player_seek(NULL, 0, SEEK_SET);
		
		formatCtx = initFormatCtx();
		if(!formatCtx) {
			printf("initFormatCtx failed\n");
			goto final;
		}
		
		int ret = av_probe_input_buffer(formatCtx->pb, &fmt, filename.c_str(), NULL, 0, formatCtx->probesize);
		if(ret < 0) {
			printf("av_probe_input_buffer failed (%s)\n", fmt ? fmt->name : "<NULL>");
			continue;
		}
		
		ret = avformat_open_input(&formatCtx, filename.c_str(), fmt, NULL);
		if(ret != 0) {
			printf("avformat_open_input (%s) failed\n", fmt->name);
			continue;
		}
		
		ret = avformat_find_stream_info(formatCtx, NULL);
		if(ret < 0) {
			printf("avformat_find_stream_info (%s) failed\n", fmt->name);
			continue;
		}
		
#ifdef DEBUG
		av_dump_format(formatCtx, 0, filename.c_str(), 0);
#endif
		
		if(formatCtx->nb_streams == 0) {
			printf("no streams found in song (%s)\n", fmt->name);
			continue;
		}
		
		ret = av_find_best_stream(formatCtx, AVMEDIA_TYPE_AUDIO, -1, -1, 0, 0);
		if(ret < 0) {
			const char* errorMsg = "unkown error";
			if(ret == AVERROR_STREAM_NOT_FOUND) errorMsg = "stream not found";
			else if(ret == AVERROR_DECODER_NOT_FOUND) errorMsg = "decoder not found";
			printf("no audio stream found in song (%s): %s\n", fmt->name, errorMsg);
			int oldloglevel = av_log_get_level();
			av_log_set_level(AV_LOG_INFO);
			av_dump_format(formatCtx, 0, filename.c_str(), 0);
			av_log_set_level(oldloglevel);
			continue;
		}
		songAudioStreamIdx = ret;
		
		ret = stream_component_open(formatCtx, songAudioStreamIdx);
		if(ret < 0) {
			printf("cannot open audio stream (%s)\n", fmt->name);
			continue;
		}
		
		if(i > 0)
			printf("fallback open succeeded (%s)\n", fmt->name);
		goto success;
	}
	printf("opening failed\n");
	goto final;
	
success:
	songCtx = formatCtx;
	formatCtx = NULL;
	
	// Get the song len: There is formatCtx.duration in AV_TIME_BASE
	// and there is stream.duration in stream time base.
	assert(songAudioStream);
	songLen = av_q2d(songAudioStream->time_base) * songAudioStream->duration;
	if(songLen < 0) {
		songLen = -1;
		printf("unknown song len\n");
	}
	else
		printf("song len: %f\n", songLen);
	
	return true;
	
final:
	if(formatCtx) closeInputStream(formatCtx);
	
	return false;
}

static void seekAbs(double pos) {
	if(pos < 0) pos = 0;
	
	int64_t seek_target = int64_t(pos * AV_TIME_BASE);
	int64_t seek_min    = 0;
	int64_t seek_max    = INT64_MAX;
	if(seek_target < 0) seek_target = INT64_MAX;
	
	int ret =
	avformat_seek_file(
					   songCtx,
					   -1, // stream
					   seek_min,
					   seek_target,
					   seek_max,
					   0 //flags
					   );
	
	if(ret < 0)
		printf("seekAbs(%f): seek failed\n", pos);
}

int main(int argc, const char** argv) {
	if(argc < 2) {
		printf("%s <mp3>\n", argv[0]);
		return 1;
	}
	const char* filename = argv[1];

	// init FFmpeg
	av_log_set_level(AV_LOG_INFO);
	avcodec_register_all();
	av_register_all();
	
	if(!openSong(filename)) return -1;
	
	// This should trigger the problem on certain mp3s.
	seekAbs(0.5);

	return 0;
}


