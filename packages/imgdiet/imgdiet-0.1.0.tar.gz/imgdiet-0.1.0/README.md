# imgdiet
A Python package for minimizing file size of images with minimal quality loss

| PNG Image                                   | WEBP Image (Optimized by `imgdiet`)                                  |
|--------------------------------------------|--------------------------------------------|
| <img src="./assets/20250105_164724.png" alt="PNG Image" width="300"> | <img src="test.webp" alt="WEBP Image" width="300"> |
| File Size: 26.9 MB                     | File Size : 4.1 MB |

## Features ✨

- **Quality Assurance**: Control over image quality using PSNR (Peak Signal-to-Noise Ratio).
- **Smart Compression**: Automatically retains the original if compression results in a larger file.
- **Folder Structure Preservation**: Maintains the original directory structure during conversion.
- **Multi-threading**: Fast processing of large batches of images.
- **ICC Profile Support**: Preserves color profiles during conversion.
- **WebP Optimization**: Leverages the latest WebP format for efficient compression.
