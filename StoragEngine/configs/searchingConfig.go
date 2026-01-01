package configs

// --- SORTING OPTIONS ---
const (
	SortNameAsc  = "name_asc"
	SortNameDesc = "name_desc"
	SortSizeAsc  = "size_asc"
	SortSizeDesc = "size_desc"
	SortDateAsc  = "date_asc"
	SortDateDesc = "date_desc" // Default
)

var ValidSortOptions = map[string]bool{
	SortNameAsc:  true,
	SortNameDesc: true,
	SortSizeAsc:  true,
	SortSizeDesc: true,
	SortDateAsc:  true,
	SortDateDesc: true,
}

// --- FILE TYPE CATEGORIES (SIMPLIFIED) ---
const (
	TypeImage = "image"
	TypeVideo = "video"
	TypeOther = "other" // Includes docs, zips, audio, text
)

var ValidFileTypes = map[string]bool{
	TypeImage: true,
	TypeVideo: true,
	TypeOther: true,
}
