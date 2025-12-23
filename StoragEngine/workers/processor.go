package workers

import (
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"storageEngine/configs"
	"storageEngine/database"
)

func StartVideoWorker(workerId int) {
	log.Printf("Video Worker %d started\n", workerId)
	// loop to process video jobs

	for job := range configs.VideoQueue {
		log.Printf("Worker %d processing video file ID: %s\n", workerId, job.FileId)
		err := ProcessVideoJob(workerId, job)
		if err != nil {
			log.Printf("Worker %d failed to process video file ID: %s, error: %v\n", workerId, job.FileId, err)
		} else {
			log.Printf("Worker %d completed processing video file ID: %s\n", workerId, job.FileId)
		}
	}
}

func ProcessVideoJob(workerId int, job configs.VideoJob) error {

	log.Printf("Worker %d started processing job for file ID: %s\n", workerId, job.FileId)

	//updae status to processing
	err := database.UpdateFileMetaDataStatus(job.FileId, configs.StatusProcessing)
	if err != nil {
		log.Printf("Worker %d failed to update status to processing for file ID: %s, error: %v\n", workerId, job.FileId, err)
		return err
	}

	//prepeare hls directory
	//input original.mp4
	//output hls segments and playlist

	hlsDir := filepath.Join(job.OutputDir, "hls")
	if err := os.MkdirAll(hlsDir, 0755); err != nil {
		log.Printf("Worker %d failed to create HLS directory for file ID: %s, error: %v\n", workerId, job.FileId, err)
		err := database.UpdateFileMetaDataStatus(job.FileId, configs.StatusFailed)
		if err != nil {
			log.Printf("Worker %d failed to update status to failed for file ID: %s, error: %v\n", workerId, job.FileId, err)
		}
		return err
	}
	hlsPath := filepath.Join(hlsDir, "index.m3u8")

	//ffmpeg -i input.mp4 -codec: copy -start_number 0 -hls_time 10 -hls_list_size 0 -f hls index.m3u8
	// Execute ffmpeg command
	// -hls_time 10: Break video into 10-second chunks
	// -hls_list_size 0: Keep all chunks in the playlist (essential for VOD)
	cmd := exec.Command("ffmpeg",
		"-i", job.SourcePath,

		// VIDEO SETTINGS
		"-c:v", "libx264",

		// OPTIMIZATION 1: Speed Preset (fast, faster, veryfast, ultrafast)
		// 'fast' is a good balance for Azure B-series VMs
		"-preset", "fast",

		// OPTIMIZATION 2: Resolution Cap (Downscale to 1080p if larger)
		// This prevents a 4K upload from killing your CPU
		// "scale='min(1920,iw)':-2" means: "If width > 1920, shrink to 1920. Else keep original."
		"-vf", "scale='min(1920,iw)':-2",

		// OPTIMIZATION 3: Constant Rate Factor (Quality Control)
		// 23 is default. 28 is lower quality but faster. 18 is visually lossless.
		"-crf", "23",

		// AUDIO SETTINGS
		"-c:a", "aac",
		"-b:a", "128k",

		// HLS SETTINGS
		"-start_number", "0",
		"-hls_time", "10",
		"-hls_list_size", "0",
		"-f", "hls",
		hlsPath,
	)
	output, err := cmd.CombinedOutput()

	if err != nil {
		log.Printf("Worker %d failed to process video for file ID: %s, error: %v, output: %s\n", workerId, job.FileId, err, string(output))
		err := database.UpdateFileMetaDataStatus(job.FileId, configs.StatusFailed)
		if err != nil {
			log.Printf("Worker %d failed to update status to failed for file ID: %s, error: %v\n", workerId, job.FileId, err)
		}
		return err
	}

	//update status to ready
	err = database.UpdateFileMetaDataStatus(job.FileId, configs.StatusReady)
	if err != nil {
		log.Printf("Worker %d failed to update status to ready for file ID: %s, error: %v\n", workerId, job.FileId, err)
		return err
	}

	log.Printf("Worker %d successfully processed video for file ID: %s\n", workerId, job.FileId)
	return nil
}
