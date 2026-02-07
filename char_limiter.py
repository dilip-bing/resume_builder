"""
Adaptive Character Limit Calculator for Resume Builder
=======================================================

Calculates pixel-accurate character limits based on actual text content.
Prevents text overflow by measuring real character widths.
"""

from PIL import Image, ImageDraw, ImageFont
import os
import json


class AdaptiveCharLimiter:
    """Calculate adaptive character limits based on pixel width."""
    
    # Font configuration matching resume format
    FONT_SIZE = 10.5
    LINE_WIDTH_INCHES = 7.87  # From metadata
    DPI = 96
    LINE_WIDTH_PIXELS = int(LINE_WIDTH_INCHES * DPI)  # 755 pixels
    
    def __init__(self):
        """Initialize the character limiter."""
        self.font = self._load_font()
        self._char_width_cache = {}
        self._calculate_char_widths()
    
    def _load_font(self):
        """Load Times New Roman font."""
        try:
            font_size_pixels = int((self.FONT_SIZE * self.DPI) / 72)
            
            # Try Windows font paths
            font_paths = [
                r'C:\Windows\Fonts\times.ttf',
                r'C:\Windows\Fonts\timesnewroman.ttf',
                r'C:\Windows\Fonts\Times New Roman.ttf',
            ]
            
            for path in font_paths:
                if os.path.exists(path):
                    return ImageFont.truetype(path, font_size_pixels)
            
            # Fallback
            return ImageFont.load_default()
            
        except Exception as e:
            print(f"Font loading warning: {e}, using default font")
            return ImageFont.load_default()
    
    def _calculate_char_widths(self):
        """Pre-calculate widths for common characters."""
        # All printable characters
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,;:!?-+*/()[]{}@#$%^&_=<>|~`"\''
        
        for char in chars:
            self._char_width_cache[char] = self._measure_char_width(char)
        
        # Find widest and narrowest
        self.widest_char_width = max(self._char_width_cache.values())
        self.narrowest_char_width = min(self._char_width_cache.values())
        self.avg_char_width = sum(self._char_width_cache.values()) / len(self._char_width_cache)
    
    def _measure_char_width(self, char):
        """Measure pixel width of a single character."""
        img = Image.new('RGB', (100, 50), color='white')
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), char, font=self.font)
        return bbox[2] - bbox[0]
    
    def get_text_width(self, text):
        """Calculate total pixel width of text string."""
        if not text:
            return 0
        
        img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), text, font=self.font)
        return bbox[2] - bbox[0]
    
    def get_initial_limit(self, prefix=""):
        """
        Get initial conservative character limit.
        
        Args:
            prefix: Fixed prefix text (e.g., "Languages: ")
        
        Returns:
            int: Initial safe character limit
        """
        prefix_width = self.get_text_width(prefix) if prefix else 0
        available_width = self.LINE_WIDTH_PIXELS - prefix_width
        
        # Use widest character for conservative estimate
        initial_limit = int(available_width / self.widest_char_width)
        
        return initial_limit
    
    def detect_num_lines(self, prefix="", original_text=""):
        """
        Detect how many lines the original text spans.
        
        Args:
            prefix: Fixed prefix
            original_text: Original text from resume
        
        Returns:
            int: Number of lines the text spans
        """
        if not original_text:
            return 1
        
        prefix_width = self.get_text_width(prefix) if prefix else 0
        text_width = self.get_text_width(original_text)
        total_width = prefix_width + text_width
        
        # Calculate number of lines (ceiling division)
        num_lines = (total_width + self.LINE_WIDTH_PIXELS - 1) // self.LINE_WIDTH_PIXELS
        return max(1, num_lines)  # At least 1 line
    
    def get_adaptive_limit(self, prefix="", current_text="", original_text="", num_lines=None):
        """
        Get adaptive character limit based on what user has typed.
        
        Args:
            prefix: Fixed prefix (e.g., "Languages: ")
            current_text: What user has typed so far
            original_text: Original text from resume (for multi-line detection)
            num_lines: Number of lines to allow (auto-detected if None)
        
        Returns:
            dict with limit info
        """
        # Auto-detect number of lines if not specified
        if num_lines is None:
            num_lines = self.detect_num_lines(prefix, original_text or current_text)
        
        # Calculate total available width (multiple lines)
        total_line_width = self.LINE_WIDTH_PIXELS * num_lines
        
        # Calculate actual width used
        prefix_width = self.get_text_width(prefix) if prefix else 0
        user_text_width = self.get_text_width(current_text) if current_text else 0
        total_width_used = prefix_width + user_text_width
        
        # Calculate remaining pixel space
        pixels_available = total_line_width - total_width_used
        
        # Calculate remaining characters (conservative)
        remaining_chars = int(pixels_available / self.widest_char_width)
        
        # Current limit = typed + remaining
        current_limit = len(current_text) + remaining_chars
        
        # Calculate efficiency
        initial_limit = self.get_initial_limit(prefix) * num_lines
        efficiency_gain = current_limit - initial_limit
        
        return {
            'current_limit': current_limit,
            'remaining': remaining_chars,
            'pixels_used': int(total_width_used),
            'pixels_available': int(pixels_available),
            'total_pixels': total_line_width,
            'percentage_used': (total_width_used / total_line_width) * 100,
            'efficiency_gain': efficiency_gain,
            'chars_typed': len(current_text),
            'is_near_limit': remaining_chars < 10,
            'is_at_limit': remaining_chars <= 0,
            'num_lines': num_lines
        }
    
    def get_field_limits(self, resume_content):
        """
        Calculate character limits for all resume fields.
        
        Args:
            resume_content: Dict from resume_content.json
        
        Returns:
            dict: Field name -> limit info
        """
        limits = {}
        
        # Skills section
        if 'skills' in resume_content:
            for skill_group in resume_content['skills']:
                label = skill_group.get('label', '')
                value = skill_group.get('value', '')
                prefix = f"{label}: " if label else ""
                
                limits[f"skill_{label.lower().replace(' ', '_')}"] = self.get_adaptive_limit(prefix, value)
        
        # Projects section
        if 'projects' in resume_content:
            for idx, project in enumerate(resume_content['projects']):
                # Project name line
                name = project.get('name', '')
                limits[f"project_{idx}_name"] = self.get_adaptive_limit("", name)
                
                # Tech stack line
                tech = project.get('tech_stack', '')
                if tech:
                    limits[f"project_{idx}_tech"] = self.get_adaptive_limit("", tech)
                
                # Bullets
                for bullet_idx, bullet in enumerate(project.get('bullets', [])):
                    limits[f"project_{idx}_bullet_{bullet_idx}"] = self.get_adaptive_limit("• ", bullet)
        
        # Professional section
        if 'professional' in resume_content:
            for idx, exp in enumerate(resume_content['professional']):
                # Tech stack
                tech = exp.get('tech_stack', '')
                if tech:
                    limits[f"professional_{idx}_tech"] = self.get_adaptive_limit("", tech)
                
                # Bullets
                for bullet_idx, bullet in enumerate(exp.get('bullets', [])):
                    limits[f"professional_{idx}_bullet_{bullet_idx}"] = self.get_adaptive_limit("• ", bullet)
        
        # Leadership section
        if 'leadership' in resume_content:
            for idx, lead in enumerate(resume_content['leadership']):
                # Bullets
                for bullet_idx, bullet in enumerate(lead.get('bullets', [])):
                    limits[f"leadership_{idx}_bullet_{bullet_idx}"] = self.get_adaptive_limit("• ", bullet)
        
        return limits


# Global instance
_limiter = None

def get_limiter():
    """Get or create global limiter instance."""
    global _limiter
    if _limiter is None:
        _limiter = AdaptiveCharLimiter()
    return _limiter


def calculate_limit(prefix="", current_text="", original_text="", num_lines=None):
    """
    Quick helper to calculate limit.
    
    Args:
        prefix: Fixed prefix text
        current_text: Current user text
        original_text: Original text from resume (for multi-line detection)
        num_lines: Number of lines to allow (auto-detected if None)
    
    Returns:
        dict: Limit information
    """
    limiter = get_limiter()
    return limiter.get_adaptive_limit(prefix, current_text, original_text, num_lines)


if __name__ == "__main__":
    # Test the limiter
    limiter = AdaptiveCharLimiter()
    
    print("="*70)
    print("ADAPTIVE CHARACTER LIMITER - Test")
    print("="*70)
    
    # Test with Languages field
    prefix = "Languages: "
    test_text = "Java, Python, C++, C, Kotlin, Swift, JavaScript, PHP, Shell Script"
    
    print(f"\nPrefix: '{prefix}'")
    print(f"Text: '{test_text}'")
    print(f"Text length: {len(test_text)} characters")
    
    info = limiter.get_adaptive_limit(prefix, test_text)
    
    print(f"\n📊 Results:")
    print(f"  Pixels used: {info['pixels_used']} / {info['total_pixels']}")
    print(f"  Percentage used: {info['percentage_used']:.1f}%")
    print(f"  Characters remaining: {info['remaining']}")
    print(f"  Current limit: {info['current_limit']}")
    print(f"  Efficiency gain: +{info['efficiency_gain']} chars")
    
    if info['is_near_limit']:
        print(f"\n⚠️  WARNING: Near character limit!")
    
    print("\n" + "="*70)
