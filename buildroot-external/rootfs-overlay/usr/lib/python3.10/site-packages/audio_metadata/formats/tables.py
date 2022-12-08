__all__ = [
	'FLACMetadataBlockType',
	'ID3PictureType',
	'ID3Version',
	'ID3v1Genres',
	'ID3v2EventTypes',
	'ID3v2FrameIDs',
	'ID3v2LyricsContentType',
	'ID3v2TimestampFormat',
	'ID3v2UnofficialFrameIDs',
	'LAMEBitrateMode',
	'LAMEChannelMode',
	'LAMEPreset',
	'LAMEReplayGainOrigin',
	'LAMEReplayGainType',
	'LAMESurroundInfo',
	'MP3BitrateMode',
	'MP3Bitrates',
	'MP3ChannelMode',
	'MP3SampleRates',
	'MP3SamplesPerFrame',
	'WAVEAudioFormat',
]

from enum import (
	Enum,
	IntEnum,
)


class _BaseEnum(Enum):
	def __repr__(self):
		return f'<{self.__class__.__name__}.{self.name}>'


class _BaseIntEnum(IntEnum):
	def __repr__(self):
		return f'<{self.__class__.__name__}.{self.name}>'


# https://xiph.org/flac/format.html#metadata_block_header
class FLACMetadataBlockType(_BaseIntEnum):
	STREAMINFO = 0
	PADDING = 1
	APPLICATION = 2
	SEEKTABLE = 3
	VORBIS_COMMENT = 4
	CUESHEET = 5
	PICTURE = 6


# http://id3.org/id3v2.3.0#Attached_picture
class ID3PictureType(_BaseIntEnum):
	OTHER = 0
	FILE_ICON = 1
	OTHER_FILE_ICON = 2
	COVER_FRONT = 3
	COVER_BACK = 4
	LEAFLET_PAGE = 5
	MEDIA = 6
	LEAD_ARTIST = 7
	ARTIST = 8
	CONDUCTOR = 9
	BAND = 10
	COMPOSER = 11
	LYRICIST = 12
	RECORDING_LOCATION = 13
	DURING_RECORDING = 14
	DURING_PERFORMANCE = 15
	SCREEN_CAPTURE = 16
	FISH = 17
	ILLUSTRATION = 18
	ARTIST_LOGOTYPE = 19
	BAND_LOGOTYPE = 19
	PUBLISHER_LOGOTYPE = 20
	STUDIO_LOGOTYPE = 20


class ID3v2EventTypes(_BaseIntEnum):
	PADDING = 0
	END_OF_INITIAL_SILENCE = 1
	INTRO_START = 2
	MAIN_PART_START = 3
	OUTRO_START = 4
	OUTRO_END = 5
	VERSE_START = 6
	REFRAIN_START = 7
	INTERLUDE_START = 8
	THEME_START = 9
	VARIATION_START = 10
	KEY_CHANGE = 11
	TIME_CHANGE = 12
	MOMENTARY_UNWANTED_NOISE = 13
	SUSTAINED_NOISE = 14
	SUSTAINED_NOISE_END = 15
	INTRO_END = 16
	MAIN_PART_END = 17
	VERSE_END = 18
	REFRAIN_END = 19
	THEME_END = 20
	PROFANITY = 21
	PROFANITY_END = 22


class ID3v2LyricsContentType(_BaseIntEnum):
	OTHER = 0
	LYRICS = 1
	TRANSCRIPTION = 2
	MOVEMENT = 3
	EVENTS = 4
	CHORD = 5
	TRIVIA = 6
	WEBPAGES = 7
	IMAGES = 8


class ID3v2TimestampFormat(_BaseIntEnum):
	MPEG_FRAMES = 0
	MILLISECONDS = 1


class ID3Version(_BaseEnum):
	v10 = (1, 0)
	v11 = (1, 1)
	v22 = (2, 2)
	v23 = (2, 3)
	v24 = (2, 4)


ID3v2FrameIDs = {
	# http://id3.org/id3v2-00
	ID3Version.v22: {
		'BUF', 'CNT', 'COM', 'CRA', 'CRM', 'ETC', 'EQU', 'IPL',
		'LNK', 'MCI', 'MLL', 'PIC', 'POP', 'REV', 'RVA', 'SLT',
		'STC', 'TAL', 'TBP', 'TCM', 'TCO', 'TCR', 'TDA', 'TDY',
		'TEN', 'TFT', 'TIM', 'TKE', 'TLA', 'TLE', 'TMT', 'TOA',
		'TOF', 'TOL', 'TOR', 'TOT', 'TP1', 'TP2', 'TP3', 'TP4',
		'TPA', 'TPB', 'TRC', 'TRD', 'TRK', 'TSI', 'TSS', 'TT1',
		'TT2', 'TT3', 'TXT', 'TXX', 'TYE', 'UFI', 'ULT', 'WAF',
		'WAR', 'WAS', 'WCM', 'WCP', 'WPB', 'WXX',
	},
	# http://id3.org/id3v2.3.0#Declared_ID3v2_frames
	ID3Version.v23: {
		'AENC', 'APIC', 'COMM', 'COMR', 'ENCR', 'EQUA', 'ETCO',
		'GEOB', 'GRID', 'IPLS', 'LINK', 'MCDI', 'MLLT', 'OWNE',
		'PRIV', 'PCNT', 'POPM', 'POSS', 'RBUF', 'RVAD', 'RVRB',
		'SYLT', 'SYTC', 'TALB', 'TBPM', 'TCOM', 'TCON', 'TCOP',
		'TDAT', 'TDLY', 'TENC', 'TEXT', 'TFLT', 'TIME', 'TIT1',
		'TIT2', 'TIT3', 'TKEY', 'TLAN', 'TLEN', 'TMED', 'TOAL',
		'TOFN', 'TOLY', 'TOPE', 'TORY', 'TOWN', 'TPE1', 'TPE2',
		'TPE3', 'TPE4', 'TPOS', 'TPUB', 'TRCK', 'TRDA', 'TRSN',
		'TRSO', 'TSIZ', 'TSRC', 'TSSE', 'TYER', 'TXXX', 'UFID',
		'USER', 'USLT', 'WCOM', 'WCOP', 'WOAF', 'WOAR', 'WOAS',
		'WORS', 'WPAY', 'WPUB', 'WXXX',
	},
	# http://id3.org/id3v2.4.0-frames
	ID3Version.v24: {
		'AENC', 'APIC', 'ASPI', 'COMM', 'COMR', 'ENCR', 'EQU2',
		'ETCO', 'GEOB', 'GRID', 'LINK', 'MCDI', 'MLLT', 'OWNE',
		'PRIV', 'PCNT', 'POPM', 'POSS', 'RBUF', 'RVA2', 'RVRB',
		'SEEK', 'SIGN', 'SYLT', 'SYTC', 'TALB', 'TBPM', 'TCOM',
		'TCON', 'TCOP', 'TDEN', 'TDLY', 'TDOR', 'TDRC', 'TDRL',
		'TDTG', 'TENC', 'TEXT', 'TFLT', 'TIPL', 'TIT1', 'TIT2',
		'TIT3', 'TKEY', 'TLAN', 'TLEN', 'TMCL', 'TMED', 'TMOO',
		'TOAL', 'TOFN', 'TOLY', 'TOPE', 'TOWN', 'TPE1', 'TPE2',
		'TPE3', 'TPE4', 'TPOS', 'TPRO', 'TPUB', 'TRCK', 'TRSN',
		'TRSO', 'TSOA', 'TSOP', 'TSOT', 'TSRC', 'TSSE', 'TSST',
		'TXXX', 'UFID', 'USER', 'USLT', 'WCOM', 'WCOP', 'WOAF',
		'WOAR', 'WOAS', 'WORS', 'WPAY', 'WPUB', 'WXXX',
	},
}

ID3v2UnofficialFrameIDs = {
	ID3Version.v22: {
		'CM1', 'PCS', 'TCP', 'TDR', 'TDS', 'TID', 'TS2', 'TSA',
		'TSC', 'TSP', 'TST', 'WFD',
	},
	ID3Version.v23: {
		'NCON', 'PCST', 'RGAD', 'TCMP', 'TDES', 'TGID', 'TKWD',
		'TSO2', 'TSOC', 'WFED', 'XDOR', 'XSOA', 'XSOP', 'XSOT',
		'XRVA',
	},
	ID3Version.v24: {
		'NCON', 'PCST', 'RGAD', 'TCMP', 'TDES', 'TGID', 'TKWD',
		'TSO2', 'TSOC', 'WFED', 'XDOR', 'XSOA', 'XSOP', 'XSOT',
		'XRVA',
	},
}


# https://en.wikipedia.org/wiki/List_of_ID3v1_Genres
ID3v1Genres = [
	'Blues',
	'Classic Rock',
	'Country',
	'Dance',
	'Disco',
	'Funk',
	'Grunge',
	'Hip-Hop',
	'Jazz',
	'Metal',
	'New Age',
	'Oldies',
	'Other',
	'Pop',
	'R&B',
	'Rap',
	'Reggae',
	'Rock',
	'Techno',
	'Industrial',
	'Alternative',
	'Ska',
	'Death Metal',
	'Pranks',
	'Soundtrack',
	'Euro-Techno',
	'Ambient',
	'Trip-Hop',
	'Vocal',
	'Jazz+Funk',
	'Fusion',
	'Trance',
	'Classical',
	'Instrumental',
	'Acid',
	'House',
	'Game',
	'Sound Clip',
	'Gospel',
	'Noise',
	'Alt Rock',
	'Bass',
	'Soul',
	'Punk',
	'Space',
	'Meditative',
	'Instrumental Pop',
	'Instrumental Rock',
	'Ethnic',
	'Gothic',
	'Darkwave',
	'Techno-Industrial',
	'Electronic',
	'Pop-Folk',
	'Eurodance',
	'Dream',
	'Southern Rock',
	'Comedy',
	'Cult',
	'Gangsta Rap',
	'Top 40',
	'Christian Rap',
	'Pop/Funk',
	'Jungle',
	'Native American',
	'Cabaret',
	'New Wave',
	'Psychedelic',
	'Rave',
	'Showtunes',
	'Trailer',
	'Lo-Fi',
	'Tribal',
	'Acid Punk',
	'Acid Jazz',
	'Polka',
	'Retro',
	'Musical',
	'Rock & Roll',
	'Hard Rock',
	'Folk',
	'Folk-Rock',
	'National Folk',
	'Swing',
	'Fast-Fusion',
	'Bebop',
	'Latin',
	'Revival',
	'Celtic',
	'Bluegrass',
	'Avantgarde',
	'Gothic Rock',
	'Progressive Rock',
	'Symphonic Rock',
	'Slow Rock',
	'Big Band',
	'Chorus',
	'Easy Listening',
	'Acoustic',
	'Humour',
	'Speech',
	'Chanson',
	'Opera',
	'Chamber Music',
	'Sonata',
	'Symphony',
	'Booty Bass',
	'Primus',
	'Porn Groove',
	'Satire',
	'Slow Jam',
	'Club',
	'Tango',
	'Samba',
	'Folklore',
	'Ballad',
	'Power Ballad',
	'Rhythmic Soul',
	'Freestyle',
	'Duet',
	'Punk Rock',
	'Drum Solo',
	'A Cappella',
	'Euro-House',
	'Dance Hall',
	'Goa',
	'Drum & Bass',
	'Club-House',
	'Hardcore',
	'Terror',
	'Indie',
	'BritPop',
	'Afro-Punk',
	'Polsk Punk',
	'Beat',
	'Christian Gangsta Rap',
	'Heavy Metal',
	'Black Metal',
	'Crossover',
	'Contemporary Christian',
	'Chrstian Rock',
	'Merengue',
	'Salsa',
	'Thrash Metal',
	'Anime',
	'JPop',
	'Synthpop',
	'Abstract',
	'Art Rock',
	'Baroque',
	'Bhangra',
	'Big Beat',
	'Breakbeat',
	'Chillout',
	'Downtempo',
	'Dub',
	'EBM',
	'Eclectic',
	'Electro',
	'Electroclash',
	'Emo',
	'Experimental',
	'Garage',
	'Global',
	'IDM',
	'Illibient',
	'Industro-Goth',
	'Jam Band',
	'Krautrock',
	'Leftfield',
	'Lounge',
	'Math Rock',
	'New Romantic',
	'Nu-Breakz',
	'Post-Punk',
	'Post-Rock',
	'Psytrance',
	'Shoegaze',
	'Space Rock',
	'Trop Rock',
	'World Music',
	'Neoclassical',
	'Audiobook',
	'Audio Theatre',
	'Neue Deutsche Welle',
	'Podcast',
	'Indie Rock',
	'G-Funk',
	'Dubstep',
	'Garage Rock',
	'Psybient',
]


class LAMEBitrateMode(_BaseIntEnum):
	UNKNOWN = 0
	CBR = 1
	ABR = 2
	VBR_METHOD_1 = 3
	VBR_METHOD_2 = 4
	VBR_METHOD_3 = 5
	VBR_METHOD_4 = 6
	CBR_2_PASS = 8
	ABR_2_PASS = 9
	RESERVED = 15


class LAMEChannelMode(_BaseIntEnum):
	MONO = 0
	STEREO = 1
	DUAL_CHANNEL = 2
	JOINT_STEREO = 3
	FORCED = 4
	AUTO = 5
	INTENSITY = 6
	UNDEFINED = 7


LAMEPreset = _BaseIntEnum(
	'LAMEPreset',
	[
		('Unknown', 0),
		*[(f'ABR{x}', x) for x in range(8, 321)],
		('V9', 410),
		('V8', 420),
		('V7', 430),
		('V6', 440),
		('V5', 450),
		('V4', 460),
		('V3', 470),
		('V2', 480),
		('V1', 490),
		('V0', 500),
		('r3mix', 1000),
		('standard', 1001),
		('extreme', 1002),
		('insane', 1003),
		('standard_fast', 1004),
		('extreme_fast', 1005),
		('medium', 1006),
		('medium_fast', 1007),
	],
)


class LAMEReplayGainOrigin(_BaseIntEnum):
	NOT_SET = 0
	ARTIST = 1
	USER = 2
	MODEL = 3
	AVERAGE = 4


class LAMEReplayGainType(_BaseIntEnum):
	NOT_SET = 0
	RADIO = 1
	AUDIOPHILE = 2


class LAMESurroundInfo(_BaseIntEnum):
	NO_SURROUND = 0
	DPL = 1
	DPL2 = 2
	AMBISONIC = 3


# (version, layer): bitrate in kilobits per second
MP3Bitrates = {
	(1, 1): [0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448],
	(1, 2): [0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384],
	(1, 3): [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
	(2, 1): [0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256],
	(2, 2): [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160],
	(2, 3): [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160],
	(2.5, 1): [0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256],
	(2.5, 2): [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160],
	(2.5, 3): [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160],
}


class MP3BitrateMode(_BaseIntEnum):
	UNKNOWN = 0
	CBR = 1
	VBR = 2
	ABR = 3


class MP3ChannelMode(_BaseIntEnum):
	STEREO = 0
	JOINT_STEREO = 1
	DUAL_CHANNEL = 2
	MONO = 3


# version
MP3SampleRates = {
	1: [44100, 48000, 32000],
	2: [22050, 24000, 16000],
	2.5: [11025, 12000, 8000],
}


# (version, layer): (samples_per_frame, slot_size)
MP3SamplesPerFrame = {
	(1, 1): (384, 4),
	(1, 2): (1152, 1),
	(1, 3): (1152, 1),
	(2, 1): (384, 4),
	(2, 2): (1152, 1),
	(2, 3): (576, 1),
	(2.5, 1): (384, 4),
	(2.5, 2): (1152, 1),
	(2.5, 3): (576, 1),
}


# http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/Docs/Pages%20from%20mmreg.h.pdf
class WAVEAudioFormat(_BaseIntEnum):
	UNKNOWN = 0
	PCM = 1
	ADPCM = 2
	IEEE_FLOAT = 3
	VSELP = 4
	IBV_CVSD = 5
	ALAW = 6
	MULAW = 7
	DTS = 8
	DRM = 9
	WMAVOICE9 = 10
	WMAVOICE10 = 11
	OKI_ADPCM = 16
	DVI_ADPCM = 17
	MEDIASPACE_ADPCM = 18
	SIERRA_ADPCM = 19
	G723_ADPCM = 20
	DIGISTD = 21
	DIGIFIX = 22
	DIALOGIC_OKI_ADPCM = 23
	MEDIAVISION_ADPCM = 24
	CU_CODEC = 25
	HP_DYN_VOICE = 26
	YAMAHA_ADPCM = 32
	SONARC = 33
	DSPGROUP_TRUESPEECH = 34
	ECHOSC1 = 35
	AUDIO_FILE_AF36 = 36
	APTX = 37
	AUDIOFILE_AF10 = 38
	PROSODY_1612 = 39
	LRC = 40
	DOLBY_AC2 = 48
	GSM610 = 49
	MSNAUDIO = 50
	ANTEX_ADPCME = 51
	CONTROL_RES_VQLPC = 52
	DIGIREAL = 53
	DIGIADPCM = 54
	CONTROL_RES_CR10 = 55
	NMS_VBXADPCM = 56
	CS_IMAADPMC = 57
	ECHOSC3 = 58
	ROCKWELL_ADPCM = 59
	ROCKWELL_DIGITALK = 60
	XEBEC = 61
	G721_ADPCM = 64
	G728_CELP = 65
	MSG723 = 66
	INTEL_G723_1 = 67
	INTEL_G729 = 68
	SHARP_G726 = 69
	MPEG = 80
	RT24 = 82
	PAC = 83
	MPEGLAYER3 = 85
	LUCENT_G723 = 89
	CIRRUS = 96
	ESPCM = 97
	VOXWARE = 98
	CANOPUS_ATRAC = 99
	G726_ADPCM = 100
	G722_ADPCM = 101
	DSAT = 102
	DSAT_DISPLAY = 103
	VOXWARE_BYTE_ALIGNED = 105
	VOXWARE_AC8 = 112
	VOXWARE_AC10 = 113
	VOXWARE_AC16 = 114
	VOXWARE_AC20 = 115
	VOXWARE_RT24 = 116
	VOXWARE_RT29 = 117
	VOXWARE_RT29HW = 118
	VOXWARE_VR12 = 119
	VOXWARE_VR18 = 120
	VOXWARE_TQ40 = 121
	VOXWARE_SC3 = 122
	VOXWARE_SC3_1 = 123
	SOFTSOUND = 128
	VOXWARE_TQ60 = 129
	MSRT24 = 130
	G729A = 131
	MVI_MVI2 = 132
	DF_G726 = 133
	DF_GSM610 = 134
	ISIAUDIO = 136
	ONLIVE = 137
	MULTITUDE_FT_SX20 = 138
	INFOCOM_ITS_G721_ADPCM = 139
	CONVEDIA_G729 = 140
	CONGRUENCY = 141
	SBC24 = 145
	DOLBY_AC3_SPDIF = 146
	MEDIASONIC_G723 = 147
	PROSODY_8KBPS = 148
	ZYXEL_ADPCM = 151
	PHILIPS_LPCBB = 152
	PACKED = 153
	MALDEN_PHONYTALK = 160
	RACAL_RECORDER_GSM = 161
	RACAL_RECORDER_G720_A = 162
	RACAL_RECORDER_G723_1 = 163
	RACAL_RECORDER_TETRA_ACELP = 164
	NEC_AAC = 176
	RAW_AAC1 = 255
	RHETOREX_ADPCM = 256
	IRAT = 257
	VIVO_G723 = 273
	VIVO_SIREN = 274
	PHILIPS_CELP = 288
	PHILIPS_GRUNDIG = 289
	DIGITAL_G723 = 291
	SANYO_LD_ADPCM = 293
	SIPROLAB_ACELPNET = 304
	SIPROLAB_ACELP4800 = 305
	SIPROLAB_ACELP8V3 = 306
	SIPROLAB_G729 = 307
	SIPROLAB_G729A = 308
	SIPROLAB_KELVIN = 309
	VOICEAGE_AMR = 310
	G726ADPCM = 320
	DICTAPHONE_CELP68 = 321
	DICTAPHONE_CELP54 = 322
	QUALCOMM_PUREVOICE = 336
	QUALCOMM_HALFRATE = 337
	TUBGSM = 341
	MSAUDIO1 = 352
	WMAUDIO2 = 353
	WMAUDIO3 = 354
	WMAUDIO_LOSSLESS = 355
	WMASPDIF = 356
	UNISYS_NAP_ADPCM = 368
	UNISYS_NAP_ULAW = 369
	UNISYS_NAP_ALAW = 370
	UNISYS_NAP_16K = 371
	SYCOM_ACM_SYC008 = 372
	SYCOM_ACM_SYC701_G726L = 373
	SYCOM_ACM_SYC701_CELP54 = 374
	SYCOM_ACM_SYC701_CELP68 = 375
	KNOWLEDGE_ADVENTURE_ADPCM = 376
	FRAUNHOFER_IIS_MPEG2_AAC = 384
	DTS_DS = 400
	CREATIVE_ADPCM = 512
	CREATIVE_FASTSPEECH8 = 514
	CREATIVE_FASTSPEECH10 = 515
	UHER_ADPCM = 528
	ULEAD_DV_AUDIO = 533
	ULEAD_DV_AUDIO_1 = 534
	QUARTERDECK = 544
	ILINK_VC = 560
	RAW_SPORT = 576
	ESST_AC3 = 577
	GENERIC_PASSTHRU = 585
	IPI_HSX = 592
	IPI_RPELP = 593
	CS2 = 608
	SONY_SCX = 624
	SONY_SCY = 625
	SONY_ATRAC3 = 626
	SONY_SPC = 627
	TELUM_AUDIO = 640
	TELUM_IA_AUDIO = 641
	NORCOM_VOICE_SYSTEMS_ADPCM = 645
	FM_TOWNS_SND = 768
	MICRONAS = 848
	MICRONAS_CELP833 = 849
	BTV_DIGITAL = 1024
	INTEL_MUSIC_CODER = 1025
	INDEO_AUDIO = 1026
	QDESIGN_MUSIC = 1104
	ON2_VP7_AUDIO = 1280
	ON2_VP6_AUDIO = 1281
	VME_VMPCM = 1664
	TPC = 1665
	LIGHTWAVE_LOSSLESS = 2222
	OLIGSM = 4096
	OLIADPCM = 4097
	OLICELP = 4098
	OLISBC = 4099
	OLIOPR = 4100
	LH_CODEC = 4352
	LH_CODEC_CELP = 4353
	LH_CODEC_SBC8 = 4354
	LH_CODEC_SBC12 = 4355
	LH_CODEC_SBC16 = 4356
	NORRIS = 5120
	ISIAUDIO_2 = 5121
	SOUNDSPACE_MUSICOMPRESS = 5376
	MPEG_ADTS_AAC = 5632
	MPEG_RAW_AAC = 5633
	MPEG_LOAS = 5634
	NOKIA_MPEG_ADTS_AAC = 5640
	NOKIA_MPEG_RAW_AAC = 5641
	VODAFONE_MPEG_ADTS_AAC = 5642
	VODAFONE_MPEG_RAW_AAC = 5643
	MPEG_HEAAC = 5648
	VOXWARE_RT24_SPEECH = 6172
	SONICFOUNDRY_LOSSLESS = 6513
	INNINGS_TELECOM_ADPCM = 6521
	LUCENT_SX8300P = 7175
	LKUCENT_SX53635 = 7180
	CUSEEME = 7939
	NTCSOFT_ALF2CM_ACM = 8132
	DVM = 8192
	DTS2 = 8193
	MAKEAVIS = 13075
	DIVIO_MPEG4_AAC = 16707
	NOKIA_ADAPTIVE_MULTIRATE = 16897
	DIVI_G726 = 16963
	LEAD_SPEECH = 17228
	LEAD_VORBIS = 22092
	WAVPACK_AUDIO = 22358
	ALAC = 27745
	OGG_VORBIS_MODE_1 = 26447
	OGG_VORBIS_MODE_2 = 26448
	OGG_VORBIS_MODE_3 = 26449
	OGG_VORBIS_MODE_1_PLUS = 26479
	OGG_VORBIS_MODE_2_PLUS = 26480
	OGG_VORBIS_MODE_3_PLUS = 26481
	NBX_3COM = 28672
	OPUS = 28751
	FAAD_AAC = 28781
	AMR_NB = 29537
	AMR_WB = 29538
	AMR_WP = 29539
	GSM_AMR_CBR = 31265
	GSM_AMR_VBR_SID = 31266
	COMVERSE_INFOSYS_G723_1 = 41216
	COMVERSE_INFOSYS_AVQSBC = 41217
	COMVERSE_INFOSYS_SBC = 41218
	SYMBOL_G729_A = 41219
	VOICEAGE_AMR_WB = 41220
	INGENIENT_G826 = 41221
	MPEG4_AAC = 41222
	ENCODE_G726 = 41223
	ZOLL_ASAO = 41224
	SPEEX_VOICE = 41225
	VIANIX_MASC = 41226
	WM9_SPECTRUM_ANALYZER = 41227
	WMF_SPECTRUM_ANALYZER = 41228
	GSM_610 = 41229
	GSM_620 = 41230
	GSM_660 = 41231
	GSM_690 = 41232
	GSM_ADAPTIVE_MULTIRATE_WB = 41233
	POLYCOM_G722 = 41234
	POLYCOM_G728 = 41235
	POLYCOM_G729_A = 41236
	POLYCOM_SIREN = 41237
	GLOBAL_IP_ILBC = 41238
	RADIOTIME_TIME_SHIFT_RADIO = 41239
	NICE_ACA = 41240
	NICE_ADPCM = 41241
	VOCORD_G721 = 41242
	VOCORD_G726 = 41243
	VOCORD_G722_1 = 41244
	VOCORD_G728 = 41245
	VOCORD_G729 = 41246
	VOCORD_G729_A = 41247
	VOCORD_G723_1 = 41248
	VOCORD_LBC = 41249
	NICE_G728 = 41250
	FRANCE_TELECOM_G729 = 41251
	CODIAN = 41252
	FLAC = 61868
	EXTENSIBLE = 65534
	DEVELOPMENT = 65535
