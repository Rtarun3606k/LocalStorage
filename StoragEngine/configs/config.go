package configs

const (
	AppName       = "Storage Engine"
	AppVersion    = "1.0.0"
	UploadDir     = "./uploads"
	MaxUploadSize = 10 << 20 // 10 MB
)

var AllowedTypes = map[string]bool{
	"image/jpeg": true,
	"image/png":  true,
	"image/gif":  true,
}
