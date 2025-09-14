"""
MitraVerify Image Analyzer
Advanced image analysis utilities for detecting manipulated content

This module provides comprehensive image analysis capabilities including
reverse image search, manipulation detection, metadata analysis, and
optical character recognition (OCR) for text extraction.
"""

import logging
import os
import hashlib
import requests
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import tempfile
import json

import numpy as np
import cv2
from PIL import Image, ImageStat, ExifTags
from PIL.ExifTags import TAGS
import pytesseract
import imagehash
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class ImageAnalyzer:
    """
    Comprehensive image analyzer for detecting manipulated content,
    extracting text, and performing reverse image searches.
    """
    
    def __init__(self):
        """Initialize the image analyzer with detection algorithms."""
        self.user_agent = UserAgent()
        
        # Image manipulation detection thresholds
        self.manipulation_thresholds = {
            'noise_variance_threshold': 100,
            'edge_density_threshold': 0.15,
            'compression_artifact_threshold': 0.3,
            'color_histogram_threshold': 0.8,
            'metadata_inconsistency_threshold': 0.7
        }
        
        # Common image manipulation indicators
        self.manipulation_patterns = self._load_manipulation_patterns()
        
        # Set up OCR (Tesseract)
        self.ocr_available = self._check_ocr_availability()
        
        logger.info("ImageAnalyzer initialized successfully")
    
    def _load_manipulation_patterns(self) -> Dict[str, Any]:
        """Load patterns that indicate image manipulation."""
        return {
            'suspicious_metadata': [
                'editing_software_signatures',
                'multiple_creation_dates',
                'missing_camera_info',
                'inconsistent_timestamps'
            ],
            'visual_artifacts': [
                'clone_stamp_patterns',
                'unnatural_edges',
                'inconsistent_lighting',
                'color_bleeding',
                'compression_inconsistencies'
            ],
            'geometric_anomalies': [
                'perspective_distortions',
                'scale_inconsistencies',
                'shadow_misalignments',
                'reflection_anomalies'
            ]
        }
    
    def _check_ocr_availability(self) -> bool:
        """Check if OCR (Tesseract) is available."""
        try:
            # Test OCR with a simple image
            test_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
            pytesseract.image_to_string(test_image)
            return True
        except Exception as e:
            logger.warning(f"OCR not available: {e}")
            return False
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive image analysis for manipulation detection.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            if not os.path.exists(image_path):
                return {'error': 'Image file not found'}
            
            # Load image
            pil_image = Image.open(image_path)
            cv_image = cv2.imread(image_path)
            
            if pil_image is None or cv_image is None:
                return {'error': 'Unable to load image'}
            
            analysis_result = {
                'file_path': image_path,
                'file_size': os.path.getsize(image_path),
                'image_dimensions': pil_image.size,
                'color_mode': pil_image.mode,
                'format': pil_image.format,
                'timestamp': datetime.now().isoformat()
            }
            
            # Metadata analysis
            analysis_result['metadata_analysis'] = self._analyze_metadata(pil_image, image_path)
            
            # Visual manipulation detection
            analysis_result['manipulation_detection'] = self._detect_visual_manipulation(cv_image, pil_image)
            
            # Compression analysis
            analysis_result['compression_analysis'] = self._analyze_compression(cv_image, image_path)
            
            # Statistical analysis
            analysis_result['statistical_analysis'] = self._analyze_image_statistics(cv_image, pil_image)
            
            # Hash analysis for duplicate detection
            analysis_result['hash_analysis'] = self._calculate_image_hashes(pil_image)
            
            # Reverse image search
            analysis_result['reverse_search_results'] = self._perform_reverse_search(image_path)
            
            # Calculate overall manipulation probability
            analysis_result['manipulation_probability'] = self._calculate_manipulation_probability(analysis_result)
            
            # Determine result and confidence
            manipulation_prob = analysis_result['manipulation_probability']
            if manipulation_prob < 0.3:
                result = 'verified'
                confidence = 1.0 - manipulation_prob
            elif manipulation_prob < 0.7:
                result = 'questionable'
                confidence = 0.6
            else:
                result = 'false'
                confidence = manipulation_prob
            
            analysis_result['result'] = result
            analysis_result['confidence_score'] = confidence
            
            # Generate manipulation indicators summary
            analysis_result['manipulation_indicators'] = self._generate_manipulation_summary(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in image analysis: {e}")
            return {
                'error': str(e),
                'result': 'error',
                'confidence_score': 0.0
            }
    
    def extract_text(self, image_path: str, languages: str = 'eng+hin') -> str:
        """
        Extract text from image using OCR.
        
        Args:
            image_path: Path to the image file
            languages: Languages for OCR (default: English + Hindi)
            
        Returns:
            Extracted text string
        """
        try:
            if not self.ocr_available:
                return "OCR not available"
            
            if not os.path.exists(image_path):
                return "Image file not found"
            
            # Load and preprocess image for OCR
            image = cv2.imread(image_path)
            if image is None:
                return "Unable to load image"
            
            # Preprocess for better OCR results
            processed_image = self._preprocess_for_ocr(image)
            
            # Configure OCR
            custom_config = f'--oem 3 --psm 6 -l {languages}'
            
            # Extract text
            extracted_text = pytesseract.image_to_string(processed_image, config=custom_config)
            
            # Clean extracted text
            cleaned_text = self._clean_extracted_text(extracted_text)
            
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error in text extraction: {e}")
            return f"Error extracting text: {str(e)}"
    
    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Remove noise
        denoised = cv2.medianBlur(gray, 5)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Threshold to binary
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        cleaned = ' '.join(text.split())
        
        # Remove very short lines (likely noise)
        lines = cleaned.split('\n')
        filtered_lines = [line.strip() for line in lines if len(line.strip()) > 2]
        
        return '\n'.join(filtered_lines)
    
    def _analyze_metadata(self, pil_image: Image.Image, image_path: str) -> Dict[str, Any]:
        """Analyze image metadata for manipulation indicators."""
        metadata_analysis = {
            'exif_data': {},
            'suspicious_indicators': [],
            'editing_software_detected': False,
            'metadata_inconsistencies': [],
            'creation_info': {}
        }
        
        try:
            # Extract EXIF data
            if hasattr(pil_image, '_getexif'):
                exif_data = pil_image._getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        metadata_analysis['exif_data'][tag] = str(value)
            
            # Check for editing software signatures
            software_indicators = [
                'Adobe Photoshop', 'GIMP', 'Paint.NET', 'Canva', 'Pixlr',
                'PhotoScape', 'Fotor', 'PicMonkey', 'Snapseed'
            ]
            
            software_field = metadata_analysis['exif_data'].get('Software', '')
            for software in software_indicators:
                if software.lower() in software_field.lower():
                    metadata_analysis['editing_software_detected'] = True
                    metadata_analysis['suspicious_indicators'].append(f'Editing software detected: {software}')
            
            # Check for missing essential metadata
            essential_fields = ['DateTime', 'Make', 'Model']
            missing_fields = [field for field in essential_fields 
                            if field not in metadata_analysis['exif_data']]
            
            if missing_fields:
                metadata_analysis['suspicious_indicators'].append(f'Missing metadata fields: {", ".join(missing_fields)}')
            
            # Check for timestamp inconsistencies
            datetime_fields = ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']
            timestamps = [metadata_analysis['exif_data'].get(field) for field in datetime_fields]
            timestamps = [ts for ts in timestamps if ts]
            
            if len(set(timestamps)) > 1:
                metadata_analysis['metadata_inconsistencies'].append('Inconsistent timestamps detected')
            
            # Extract creation information
            metadata_analysis['creation_info'] = {
                'camera_make': metadata_analysis['exif_data'].get('Make', 'Unknown'),
                'camera_model': metadata_analysis['exif_data'].get('Model', 'Unknown'),
                'creation_date': metadata_analysis['exif_data'].get('DateTime', 'Unknown'),
                'gps_info': 'GPS' in metadata_analysis['exif_data']
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing metadata: {e}")
            metadata_analysis['error'] = str(e)
        
        return metadata_analysis
    
    def _detect_visual_manipulation(self, cv_image: np.ndarray, pil_image: Image.Image) -> Dict[str, Any]:
        """Detect visual indicators of image manipulation."""
        manipulation_detection = {
            'noise_analysis': {},
            'edge_analysis': {},
            'color_analysis': {},
            'texture_analysis': {},
            'suspicious_regions': [],
            'manipulation_indicators': []
        }
        
        try:
            # Noise analysis
            manipulation_detection['noise_analysis'] = self._analyze_noise_patterns(cv_image)
            
            # Edge analysis
            manipulation_detection['edge_analysis'] = self._analyze_edge_patterns(cv_image)
            
            # Color analysis
            manipulation_detection['color_analysis'] = self._analyze_color_patterns(cv_image, pil_image)
            
            # Texture analysis
            manipulation_detection['texture_analysis'] = self._analyze_texture_patterns(cv_image)
            
            # Detect suspicious regions
            manipulation_detection['suspicious_regions'] = self._detect_suspicious_regions(cv_image)
            
            # Compile manipulation indicators
            manipulation_detection['manipulation_indicators'] = self._compile_visual_indicators(manipulation_detection)
            
        except Exception as e:
            logger.warning(f"Error in visual manipulation detection: {e}")
            manipulation_detection['error'] = str(e)
        
        return manipulation_detection
    
    def _analyze_noise_patterns(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze noise patterns that might indicate manipulation."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate noise variance
        noise = cv2.Laplacian(gray, cv2.CV_64F)
        noise_variance = noise.var()
        
        # Analyze noise distribution
        noise_mean = np.mean(np.abs(noise))
        noise_std = np.std(noise)
        
        return {
            'noise_variance': float(noise_variance),
            'noise_mean': float(noise_mean),
            'noise_std': float(noise_std),
            'suspicious': noise_variance > self.manipulation_thresholds['noise_variance_threshold']
        }
    
    def _analyze_edge_patterns(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze edge patterns for manipulation indicators."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect edges
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        # Analyze edge continuity
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        avg_contour_length = np.mean([cv2.arcLength(contour, True) for contour in contours]) if contours else 0
        
        return {
            'edge_density': float(edge_density),
            'num_contours': len(contours),
            'avg_contour_length': float(avg_contour_length),
            'suspicious': edge_density > self.manipulation_thresholds['edge_density_threshold']
        }
    
    def _analyze_color_patterns(self, cv_image: np.ndarray, pil_image: Image.Image) -> Dict[str, Any]:
        """Analyze color patterns for manipulation indicators."""
        # Color histogram analysis
        hist_b = cv2.calcHist([cv_image], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([cv_image], [1], None, [256], [0, 256])
        hist_r = cv2.calcHist([cv_image], [2], None, [256], [0, 256])
        
        # Calculate histogram entropy
        hist_entropy = self._calculate_histogram_entropy([hist_b, hist_g, hist_r])
        
        # Color distribution analysis using PIL
        stat = ImageStat.Stat(pil_image)
        color_mean = stat.mean
        color_stddev = stat.stddev
        
        # Check for unnatural color distributions
        color_variance = np.var(color_mean)
        
        return {
            'histogram_entropy': float(hist_entropy),
            'color_mean': color_mean,
            'color_stddev': color_stddev,
            'color_variance': float(color_variance),
            'suspicious': hist_entropy < self.manipulation_thresholds['color_histogram_threshold']
        }
    
    def _calculate_histogram_entropy(self, histograms: List[np.ndarray]) -> float:
        """Calculate entropy of color histograms."""
        total_entropy = 0
        for hist in histograms:
            hist_norm = hist / np.sum(hist)
            hist_norm = hist_norm[hist_norm > 0]  # Remove zeros to avoid log(0)
            entropy = -np.sum(hist_norm * np.log2(hist_norm))
            total_entropy += entropy
        return total_entropy / len(histograms)
    
    def _analyze_texture_patterns(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze texture patterns for manipulation indicators."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Local Binary Pattern (simplified)
        lbp = self._calculate_lbp(gray)
        lbp_variance = np.var(lbp)
        
        # Texture energy using Gray-Level Co-occurrence Matrix (simplified)
        texture_energy = self._calculate_texture_energy(gray)
        
        return {
            'lbp_variance': float(lbp_variance),
            'texture_energy': float(texture_energy),
            'texture_uniformity': float(np.mean(lbp)),
            'suspicious': lbp_variance < 10  # Very uniform texture might indicate manipulation
        }
    
    def _calculate_lbp(self, image: np.ndarray, radius: int = 1, n_points: int = 8) -> np.ndarray:
        """Calculate simplified Local Binary Pattern."""
        # Simplified LBP implementation
        h, w = image.shape
        lbp_image = np.zeros((h, w), dtype=np.uint8)
        
        for i in range(radius, h - radius):
            for j in range(radius, w - radius):
                center = image[i, j]
                binary_string = ''
                
                # Check 8 neighboring pixels
                neighbors = [
                    image[i-1, j-1], image[i-1, j], image[i-1, j+1],
                    image[i, j+1], image[i+1, j+1], image[i+1, j],
                    image[i+1, j-1], image[i, j-1]
                ]
                
                for neighbor in neighbors:
                    binary_string += '1' if neighbor >= center else '0'
                
                lbp_image[i, j] = int(binary_string, 2)
        
        return lbp_image
    
    def _calculate_texture_energy(self, image: np.ndarray) -> float:
        """Calculate texture energy (simplified)."""
        # Use Sobel operators to detect texture
        sobel_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
        
        gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        texture_energy = np.mean(gradient_magnitude)
        
        return texture_energy
    
    def _detect_suspicious_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect regions that might have been manipulated."""
        suspicious_regions = []
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect regions with inconsistent noise levels
            # Divide image into blocks and analyze each
            h, w = gray.shape
            block_size = 64
            
            noise_levels = []
            for y in range(0, h - block_size, block_size):
                for x in range(0, w - block_size, block_size):
                    block = gray[y:y+block_size, x:x+block_size]
                    noise = cv2.Laplacian(block, cv2.CV_64F)
                    noise_level = noise.var()
                    noise_levels.append((noise_level, x, y))
            
            # Find outlier blocks
            if noise_levels:
                noise_values = [nl[0] for nl in noise_levels]
                mean_noise = np.mean(noise_values)
                std_noise = np.std(noise_values)
                threshold = mean_noise + 2 * std_noise
                
                for noise_level, x, y in noise_levels:
                    if noise_level > threshold:
                        suspicious_regions.append({
                            'type': 'inconsistent_noise',
                            'location': {'x': x, 'y': y, 'width': block_size, 'height': block_size},
                            'confidence': min((noise_level - mean_noise) / std_noise / 2, 1.0)
                        })
        
        except Exception as e:
            logger.warning(f"Error detecting suspicious regions: {e}")
        
        return suspicious_regions
    
    def _compile_visual_indicators(self, detection_results: Dict[str, Any]) -> List[str]:
        """Compile visual manipulation indicators."""
        indicators = []
        
        # Check noise analysis
        noise_analysis = detection_results.get('noise_analysis', {})
        if noise_analysis.get('suspicious', False):
            indicators.append('Suspicious noise patterns detected')
        
        # Check edge analysis
        edge_analysis = detection_results.get('edge_analysis', {})
        if edge_analysis.get('suspicious', False):
            indicators.append('Unusual edge patterns detected')
        
        # Check color analysis
        color_analysis = detection_results.get('color_analysis', {})
        if color_analysis.get('suspicious', False):
            indicators.append('Abnormal color distribution detected')
        
        # Check texture analysis
        texture_analysis = detection_results.get('texture_analysis', {})
        if texture_analysis.get('suspicious', False):
            indicators.append('Inconsistent texture patterns detected')
        
        # Check suspicious regions
        suspicious_regions = detection_results.get('suspicious_regions', [])
        if suspicious_regions:
            indicators.append(f'{len(suspicious_regions)} suspicious regions detected')
        
        return indicators
    
    def _analyze_compression(self, image: np.ndarray, image_path: str) -> Dict[str, Any]:
        """Analyze compression artifacts and quality."""
        compression_analysis = {
            'file_size': os.path.getsize(image_path),
            'compression_ratio': 0.0,
            'quality_estimate': 0.0,
            'artifacts_detected': False,
            'recompression_evidence': False
        }
        
        try:
            # Estimate JPEG quality (simplified)
            file_size = compression_analysis['file_size']
            pixel_count = image.shape[0] * image.shape[1]
            bytes_per_pixel = file_size / pixel_count
            
            # Rough quality estimation based on file size
            if bytes_per_pixel > 2:
                quality_estimate = 95
            elif bytes_per_pixel > 1.5:
                quality_estimate = 85
            elif bytes_per_pixel > 1:
                quality_estimate = 75
            elif bytes_per_pixel > 0.5:
                quality_estimate = 60
            else:
                quality_estimate = 40
            
            compression_analysis['quality_estimate'] = quality_estimate
            compression_analysis['bytes_per_pixel'] = bytes_per_pixel
            
            # Detect compression artifacts
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Look for blocking artifacts (8x8 DCT blocks in JPEG)
            block_variance = self._detect_blocking_artifacts(gray)
            compression_analysis['block_variance'] = float(block_variance)
            compression_analysis['artifacts_detected'] = block_variance > 50
            
        except Exception as e:
            logger.warning(f"Error analyzing compression: {e}")
            compression_analysis['error'] = str(e)
        
        return compression_analysis
    
    def _detect_blocking_artifacts(self, gray_image: np.ndarray) -> float:
        """Detect JPEG blocking artifacts."""
        h, w = gray_image.shape
        block_variances = []
        
        # Analyze 8x8 blocks (JPEG standard)
        for y in range(0, h - 8, 8):
            for x in range(0, w - 8, 8):
                block = gray_image[y:y+8, x:x+8]
                block_variances.append(np.var(block))
        
        # High variance in block boundaries indicates artifacts
        return np.var(block_variances) if block_variances else 0
    
    def _analyze_image_statistics(self, cv_image: np.ndarray, pil_image: Image.Image) -> Dict[str, Any]:
        """Analyze statistical properties of the image."""
        statistical_analysis = {
            'color_statistics': {},
            'brightness_statistics': {},
            'contrast_statistics': {},
            'sharpness_estimate': 0.0
        }
        
        try:
            # Color channel statistics
            b, g, r = cv2.split(cv_image)
            statistical_analysis['color_statistics'] = {
                'red_mean': float(np.mean(r)),
                'green_mean': float(np.mean(g)),
                'blue_mean': float(np.mean(b)),
                'red_std': float(np.std(r)),
                'green_std': float(np.std(g)),
                'blue_std': float(np.std(b))
            }
            
            # Brightness analysis
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            statistical_analysis['brightness_statistics'] = {
                'mean_brightness': float(np.mean(gray)),
                'brightness_std': float(np.std(gray)),
                'brightness_range': float(np.max(gray) - np.min(gray))
            }
            
            # Contrast analysis
            contrast = np.std(gray)
            statistical_analysis['contrast_statistics'] = {
                'rms_contrast': float(contrast),
                'michelson_contrast': float((np.max(gray) - np.min(gray)) / (np.max(gray) + np.min(gray))) if np.max(gray) + np.min(gray) > 0 else 0
            }
            
            # Sharpness estimation using Laplacian variance
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()
            statistical_analysis['sharpness_estimate'] = float(sharpness)
            
        except Exception as e:
            logger.warning(f"Error in statistical analysis: {e}")
            statistical_analysis['error'] = str(e)
        
        return statistical_analysis
    
    def _calculate_image_hashes(self, pil_image: Image.Image) -> Dict[str, str]:
        """Calculate various image hashes for duplicate detection."""
        hash_analysis = {}
        
        try:
            # Different hash algorithms for different purposes
            hash_analysis['average_hash'] = str(imagehash.average_hash(pil_image))
            hash_analysis['perceptual_hash'] = str(imagehash.phash(pil_image))
            hash_analysis['difference_hash'] = str(imagehash.dhash(pil_image))
            hash_analysis['wavelet_hash'] = str(imagehash.whash(pil_image))
            
            # MD5 hash of image data
            import hashlib
            image_bytes = pil_image.tobytes()
            hash_analysis['md5_hash'] = hashlib.md5(image_bytes).hexdigest()
            
        except Exception as e:
            logger.warning(f"Error calculating hashes: {e}")
            hash_analysis['error'] = str(e)
        
        return hash_analysis
    
    def _perform_reverse_search(self, image_path: str) -> List[Dict[str, Any]]:
        """Perform reverse image search (simplified mock implementation)."""
        # Note: In production, this would integrate with actual reverse search APIs
        reverse_search_results = []
        
        try:
            # Mock reverse search results
            # In reality, you would use Google Images API, TinEye API, etc.
            reverse_search_results = [
                {
                    'source': 'mock_search_engine',
                    'url': 'https://example.com/similar-image',
                    'title': 'Similar image found',
                    'date': '2023-01-01',
                    'similarity_score': 0.85,
                    'context': 'Found in news article about...'
                }
            ]
            
            # Here you would implement actual API calls to:
            # - Google Images Reverse Search
            # - TinEye API
            # - Bing Visual Search
            # - Yandex Images
            
        except Exception as e:
            logger.warning(f"Error in reverse search: {e}")
            reverse_search_results = [{'error': str(e)}]
        
        return reverse_search_results
    
    def _calculate_manipulation_probability(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate overall probability that image has been manipulated."""
        try:
            probability_factors = []
            
            # Factor 1: Metadata suspicious indicators
            metadata = analysis_result.get('metadata_analysis', {})
            suspicious_metadata = len(metadata.get('suspicious_indicators', []))
            if suspicious_metadata > 0:
                probability_factors.append(min(suspicious_metadata * 0.2, 0.6))
            
            # Factor 2: Visual manipulation indicators
            visual = analysis_result.get('manipulation_detection', {})
            visual_indicators = len(visual.get('manipulation_indicators', []))
            if visual_indicators > 0:
                probability_factors.append(min(visual_indicators * 0.15, 0.5))
            
            # Factor 3: Compression inconsistencies
            compression = analysis_result.get('compression_analysis', {})
            if compression.get('artifacts_detected', False):
                probability_factors.append(0.3)
            
            # Factor 4: Statistical anomalies
            stats = analysis_result.get('statistical_analysis', {})
            sharpness = stats.get('sharpness_estimate', 100)
            if sharpness < 50:  # Very low sharpness might indicate manipulation
                probability_factors.append(0.2)
            
            # Factor 5: Suspicious regions
            visual_detection = analysis_result.get('manipulation_detection', {})
            suspicious_regions = visual_detection.get('suspicious_regions', [])
            if suspicious_regions:
                probability_factors.append(min(len(suspicious_regions) * 0.1, 0.4))
            
            # Calculate weighted average
            if probability_factors:
                # Use maximum of factors rather than average for conservative estimation
                manipulation_probability = max(probability_factors)
                # Apply some smoothing
                manipulation_probability = min(manipulation_probability * 1.2, 1.0)
            else:
                manipulation_probability = 0.1  # Low baseline probability
            
            return manipulation_probability
            
        except Exception as e:
            logger.error(f"Error calculating manipulation probability: {e}")
            return 0.5  # Return neutral probability on error
    
    def _generate_manipulation_summary(self, analysis_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate summary of manipulation indicators."""
        indicators = []
        
        # Metadata indicators
        metadata = analysis_result.get('metadata_analysis', {})
        for indicator in metadata.get('suspicious_indicators', []):
            indicators.append({
                'type': 'metadata',
                'description': indicator,
                'severity': 'medium'
            })
        
        # Visual indicators
        visual = analysis_result.get('manipulation_detection', {})
        for indicator in visual.get('manipulation_indicators', []):
            indicators.append({
                'type': 'visual',
                'description': indicator,
                'severity': 'high' if 'suspicious' in indicator.lower() else 'medium'
            })
        
        # Compression indicators
        compression = analysis_result.get('compression_analysis', {})
        if compression.get('artifacts_detected', False):
            indicators.append({
                'type': 'compression',
                'description': 'JPEG compression artifacts detected',
                'severity': 'low'
            })
        
        return indicators
    
    def compare_images(self, image_path1: str, image_path2: str) -> Dict[str, Any]:
        """Compare two images for similarity and potential manipulation relationship."""
        try:
            # Load images
            img1 = Image.open(image_path1)
            img2 = Image.open(image_path2)
            
            # Calculate hashes
            hash1 = {
                'average': imagehash.average_hash(img1),
                'perceptual': imagehash.phash(img1),
                'difference': imagehash.dhash(img1)
            }
            
            hash2 = {
                'average': imagehash.average_hash(img2),
                'perceptual': imagehash.phash(img2),
                'difference': imagehash.dhash(img2)
            }
            
            # Calculate similarities
            similarities = {}
            for hash_type in hash1:
                similarity = 1 - (hash1[hash_type] - hash2[hash_type]) / 64.0  # Normalize
                similarities[f'{hash_type}_similarity'] = max(0, similarity)
            
            # Overall similarity
            overall_similarity = np.mean(list(similarities.values()))
            
            # Determine relationship
            if overall_similarity > 0.95:
                relationship = 'identical_or_minimal_changes'
            elif overall_similarity > 0.8:
                relationship = 'very_similar_possible_manipulation'
            elif overall_similarity > 0.6:
                relationship = 'similar_content_different_processing'
            else:
                relationship = 'different_images'
            
            return {
                'overall_similarity': float(overall_similarity),
                'hash_similarities': {k: float(v) for k, v in similarities.items()},
                'relationship': relationship,
                'manipulation_likelihood': max(0, 0.8 - overall_similarity) if overall_similarity < 0.8 else 0
            }
            
        except Exception as e:
            logger.error(f"Error comparing images: {e}")
            return {'error': str(e)}
    
    def get_analyzer_stats(self) -> Dict[str, Any]:
        """Get statistics about the analyzer's capabilities."""
        return {
            'ocr_available': self.ocr_available,
            'supported_formats': ['JPEG', 'PNG', 'BMP', 'TIFF', 'WebP'],
            'detection_features': [
                'Metadata analysis',
                'Visual manipulation detection',
                'Compression analysis',
                'Statistical analysis',
                'Hash-based duplicate detection',
                'OCR text extraction',
                'Reverse image search integration'
            ],
            'manipulation_patterns': len(sum(self.manipulation_patterns.values(), [])),
            'hash_algorithms': ['Average Hash', 'Perceptual Hash', 'Difference Hash', 'Wavelet Hash', 'MD5'],
            'ocr_languages': ['eng', 'hin', 'tam', 'ben', 'mar'] if self.ocr_available else []
        }
