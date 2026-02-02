# Artistic Styles Reference

Complete guide to all 10 artistic text styles available in the video orchestrator.

## Available Styles

### 1. gradient_3d (Gradient 3D)
**Description**: Pink to blue gradient with 3D depth shadows  
**Best for**: Modern, vibrant content  
**Colors**: Pink → Blue gradient  
**Effects**: 3D shadow layers, white outline  

```bash
uv run python video_orchestrator.py --artistic-style gradient_3d "URL"
```

### 2. neon_glow (Neon Glow)
**Description**: Cyan neon light effect with multiple glow layers  
**Best for**: Night scenes, electronic/tech content  
**Colors**: Cyan/Turquoise  
**Effects**: Multi-layer glow, blur effects  

```bash
uv run python video_orchestrator.py --artistic-style neon_glow "URL"
```

### 3. metallic_gold (Metallic Gold)
**Description**: Luxurious gold metallic finish  
**Best for**: Premium content, celebrations, achievements  
**Colors**: Gold (RGB: 255, 215, 0)  
**Effects**: Metallic gradient, bright highlights  

```bash
uv run python video_orchestrator.py --artistic-style metallic_gold "URL"
```

### 4. rainbow_3d (Rainbow 3D)
**Description**: Full spectrum rainbow gradient with 3D depth  
**Best for**: Colorful, fun, energetic content  
**Colors**: Full HSV spectrum (Red → Violet)  
**Effects**: 3D shadows, rainbow gradient  

```bash
uv run python video_orchestrator.py --artistic-style rainbow_3d "URL"
```

### 5. crystal_ice (Crystal Ice) ⭐ DEFAULT
**Description**: Ice blue crystal effect with transparency  
**Best for**: Cool, calm, professional content  
**Colors**: Ice blue (RGB: 200-255, 230-255, 255)  
**Effects**: Gradient, highlights, shadows  

```bash
uv run python video_orchestrator.py --artistic-style crystal_ice "URL"
# or simply:
uv run python video_orchestrator.py "URL"
```

### 6. fire_flame (Fire Flame)
**Description**: Hot flame effect with orange-red gradient  
**Best for**: Action, intense, dramatic content  
**Colors**: Red → Orange → Yellow gradient  
**Effects**: Flame gradient, orange glow  

```bash
uv run python video_orchestrator.py --artistic-style fire_flame "URL"
```

### 7. metallic_silver (Metallic Silver)
**Description**: Sleek silver metallic finish  
**Best for**: Tech, modern, sophisticated content  
**Colors**: Silver gray with wave pattern  
**Effects**: Metallic sheen, highlights, shadows  

```bash
uv run python video_orchestrator.py --artistic-style metallic_silver "URL"
```

### 8. glowing_plasma (Glowing Plasma)
**Description**: Purple-pink plasma energy effect  
**Best for**: Sci-fi, futuristic, energy themes  
**Colors**: Purple, Pink, Magenta  
**Effects**: Plasma waves, outer glow  

```bash
uv run python video_orchestrator.py --artistic-style glowing_plasma "URL"
```

### 9. stone_carved (Stone Carved)
**Description**: Carved stone texture effect  
**Best for**: Historical, ancient, solid themes  
**Colors**: Gray stone with texture noise  
**Effects**: Carved depth, stone texture  

```bash
uv run python video_orchestrator.py --artistic-style stone_carved "URL"
```

### 10. glass_transparent (Glass Transparent)
**Description**: Semi-transparent glass effect  
**Best for**: Elegant, subtle, modern content  
**Colors**: Light blue-white (semi-transparent)  
**Effects**: Glass transparency, highlights, borders  

```bash
uv run python video_orchestrator.py --artistic-style glass_transparent "URL"
```

## Style Comparison Matrix

| Style | Brightness | Contrast | Complexity | Best Use Case |
|-------|-----------|----------|------------|---------------|
| gradient_3d | High | High | Medium | Modern/Vibrant |
| neon_glow | Very High | Very High | High | Night/Tech |
| metallic_gold | High | Medium | Medium | Premium/Luxury |
| rainbow_3d | Very High | High | High | Fun/Colorful |
| crystal_ice | Medium | Medium | Medium | Professional |
| fire_flame | Very High | Very High | High | Action/Drama |
| metallic_silver | Medium | Medium | Medium | Tech/Modern |
| glowing_plasma | High | High | High | Sci-fi/Energy |
| stone_carved | Low | Low | Low | Historical |
| glass_transparent | Low | Low | Low | Elegant/Subtle |

## Technical Details

### Rendering Techniques

All styles use:
- **NumPy** for fast gradient generation
- **PIL/Pillow** for image composition
- **Alpha compositing** for layering effects
- **Font caching** for performance

### Performance

Rendering time per clip (approximate):
- Simple styles (stone_carved, glass_transparent): ~8-10 seconds
- Medium styles (crystal_ice, metallic_gold, metallic_silver): ~10-12 seconds
- Complex styles (neon_glow, rainbow_3d, glowing_plasma, fire_flame): ~12-15 seconds

### Font Support

All styles automatically detect and use Chinese fonts:
- macOS: STHeiti, PingFang
- Windows: SimSun, Microsoft YaHei
- Linux: DejaVu Sans (fallback)

## Usage Examples

### Try all styles on same video

```bash
# Generate clips once
uv run python video_orchestrator.py --no-titles "URL"

# Then try different styles
for style in gradient_3d neon_glow metallic_gold rainbow_3d crystal_ice \
             fire_flame metallic_silver glowing_plasma stone_carved glass_transparent; do
    uv run python video_orchestrator.py --skip-analysis --artistic-style $style "URL"
done
```

### Compare two styles

```bash
# Style 1: Crystal ice
uv run python video_orchestrator.py --artistic-style crystal_ice "URL"

# Style 2: Fire flame (skip analysis, reuse clips)
uv run python video_orchestrator.py --skip-analysis --artistic-style fire_flame "URL"
```

### Custom workflow

```bash
# Step 1: Full analysis and clip generation
uv run python video_orchestrator.py --no-titles "URL"

# Step 2: Add titles with your favorite style
uv run python video_orchestrator.py --skip-analysis --no-clips --artistic-style neon_glow "URL"
```

## Style Selection Guide

### By Content Type

**Gaming/Esports**: neon_glow, fire_flame, glowing_plasma  
**Business/Professional**: crystal_ice, metallic_silver, glass_transparent  
**Entertainment/Fun**: rainbow_3d, gradient_3d, neon_glow  
**Luxury/Premium**: metallic_gold, metallic_silver  
**Historical/Documentary**: stone_carved, glass_transparent  
**Tech/Science**: neon_glow, glowing_plasma, metallic_silver  
**Action/Sports**: fire_flame, rainbow_3d, gradient_3d  

### By Mood

**Energetic**: fire_flame, rainbow_3d, neon_glow  
**Calm**: crystal_ice, glass_transparent  
**Professional**: metallic_silver, crystal_ice  
**Fun**: rainbow_3d, gradient_3d  
**Dramatic**: fire_flame, glowing_plasma  
**Elegant**: glass_transparent, metallic_gold  

### By Visibility

**High contrast (easy to read)**: neon_glow, fire_flame, metallic_gold  
**Medium contrast**: gradient_3d, rainbow_3d, crystal_ice  
**Low contrast (subtle)**: glass_transparent, stone_carved  

## Customization

To add your own style:

1. Add method to `ArtisticTextRenderer` class in `title_adder.py`:
```python
def _create_my_style(self, text, font, img_width, img_height, x_pos, y_pos):
    """My custom style"""
    # Your rendering code here
    return np.array(final_img)
```

2. Add to `style_methods` dictionary:
```python
style_methods = {
    # ... existing styles ...
    'my_style': self._create_my_style,
}
```

3. Add to CLI choices in `video_orchestrator.py`:
```python
choices=['gradient_3d', ..., 'my_style']
```

## Tips

1. **Preview first**: Test on one clip before processing all
2. **Consider background**: Choose style that contrasts with video content
3. **Match theme**: Align style with video mood/topic
4. **Readability**: Prioritize legibility over aesthetics
5. **Consistency**: Use same style for related videos

## Troubleshooting

**Text too small**: Styles use 40px font by default (configurable in code)  
**Colors don't match**: Edit RGB values in style method  
**Rendering slow**: Use simpler styles or reduce video resolution  
**Font issues**: Check font detection in logs, install Chinese fonts if needed  

## See Also

- `ARTISTIC_TITLES_GUIDE.md` - Original artistic titles documentation
- `QUICK_START_GUIDE.md` - General usage guide
- `README_orchestrator_updates.md` - Technical documentation
