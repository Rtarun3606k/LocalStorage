package configs

const (
	AppName            = "Storage Engine"
	AppVersion         = "1.0.0"
	UploadDir          = "./uploads"
	MaxUploadSize      = 10 << 20  // 10 MB
	MaxUploadSizeVideo = 200 << 20 // 200 MB
	StatusPending      = "pending"
	StatusProcessing   = "processing"
	StatusReady        = "ready"
	StatusFailed       = "failed"
	NumVideoWorkers    = 3 // Number of concurrent video processing workers
)

var AllowedTypes = map[string]bool{
	"image/jpeg": true,
	"image/png":  true,
	"image/gif":  true,
	"video/mp4":  true,
	"video/mpeg": true,
	"video/webm": true,
}

type VideoJob struct {
	FileId     string
	SourcePath string
	OutputDir  string
}

var VideoQueue = make(chan VideoJob, 100) // Buffered channel for video jobs limiting 100 jobs
