package configs

import "regexp"

var SafeRegex = regexp.MustCompile(`[^a-zA-Z0-9 ._-]`)

const (
	AppName            = "Storage Engine"
	AppVersion         = "1.0.0"
	UploadDir          = "./uploads"
	MaxUploadSize      = 10 << 20  // 10 MB
	MaxUploadSizeVideo = 200 << 20 // 200 MB
	MaxUploadSizeOther = 500 << 20 // 500 MB
	StatusPending      = "pending"
	StatusProcessing   = "processing"
	StatusReady        = "ready"
	StatusFailed       = "failed"
	NumVideoWorkers    = 3 // Number of concurrent video processing workers
)

var AllowedTypes = map[string]bool{
	// --- IMAGES ---
	"image/jpeg":    true, // .jpg, .jpeg
	"image/png":     true, // .png
	"image/gif":     true, // .gif
	"image/webp":    true, // .webp (modern web images)
	"image/svg+xml": true, // .svg (vector graphics)

	// --- VIDEO ---
	"video/mp4":       true, // .mp4
	"video/mpeg":      true, // .mpeg
	"video/webm":      true, // .webm
	"video/avi":       true, // .avi
	"video/x-msvideo": true, // .avi (windows sometimes sends this)
	"video/quicktime": true, // .mov (mac/iphone recordings)

	// --- DOCUMENTS (Reports, Assignments) ---
	"application/pdf":   true, // .pdf
	"application/x-pdf": true, // .pdf (older browsers)

	// Microsoft Word
	"application/msword": true, // .doc (legacy)
	"application/vnd.openxmlformats-officedocument.wordprocessingml.document": true, // .docx

	// Microsoft Excel (Data Engineering)
	"application/vnd.ms-excel": true, // .xls (legacy)
	"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": true, // .xlsx

	// Microsoft PowerPoint (Presentations)
	"application/vnd.ms-powerpoint":                                             true, // .ppt (legacy)
	"application/vnd.openxmlformats-officedocument.presentationml.presentation": true, // .pptx

	// --- ARCHIVES (Project Submissions) ---
	"application/zip":              true, // .zip
	"application/x-zip-compressed": true, // .zip (windows variation)
	"application/x-rar-compressed": true, // .rar
	"application/gzip":             true, // .tar.gz (Linux/CS projects)
	"application/x-tar":            true, // .tar

	// --- CODE & TEXT (CS/Engineering) ---
	"text/plain":       true, // .txt, .c, .py, .java, .go, .md (CRITICAL for code)
	"text/csv":         true, // .csv (Data Science/ML datasets)
	"application/json": true, // .json (Config files)
	"application/xml":  true, // .xml
	"text/xml":         true, // .xml
	"text/markdown":    true, // .md (Readme files)

	// --- WEB DEVELOPMENT ---
	"text/html":              true, // .html
	"text/css":               true, // .css
	"text/javascript":        true, // .js
	"application/javascript": true, // .js
}

type VideoJob struct {
	FileId     string
	SourcePath string
	OutputDir  string
}

var VideoQueue = make(chan VideoJob, 100) // Buffered channel for video jobs limiting 100 jobs
