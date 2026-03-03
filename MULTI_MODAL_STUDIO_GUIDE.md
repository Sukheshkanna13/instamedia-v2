# Multi-Modal Creative Studio - User Guide

**Quick reference for generating images, carousels, and video storyboards**

---

## 🎨 What Can You Create?

### 1. Single Image
Generate one high-quality image (1024x1024) for your post.

**Best for**: Instagram posts, LinkedIn posts, Twitter images

**Example**:
- Caption: "The mistake that almost ended our startup"
- Result: 1 professional image in ~20 seconds

### 2. Carousel (3-5 Slides)
Generate a multi-slide carousel with cohesive storytelling.

**Best for**: Instagram carousels, LinkedIn documents, educational content

**Example**:
- Caption: "5 lessons from failing 10 times"
- Result: 5 slides with titles, content, and images in ~25 seconds

### 3. Video Storyboard (5-8 Scenes)
Generate a scene-by-scene storyboard with keyframe images.

**Best for**: Instagram Reels, TikTok, YouTube Shorts planning

**Example**:
- Caption: "Day in the life of a founder"
- Result: 6 scenes with descriptions and keyframes in ~25 seconds

---

## 🚀 How to Use

### Step 1: Write Your Content
1. Go to **Creative Studio** tab
2. Enter your topic/idea
3. Click **Generate Post** to create caption and hashtags

### Step 2: Open Media Generator
1. Scroll down to **Media Generator** section
2. Click **Show** to expand

### Step 3: Select Format
Choose one:
- 🖼 **Image** - Single high-quality image
- 📱 **Carousel** - 3-5 slides
- 🎬 **Video** - 5-8 scene storyboard

### Step 4: Generate
1. Click **Generate [Format]** button
2. Wait 20-30 seconds (shows progress)
3. View your generated media

### Step 5: Use Your Media
- **Download** images for use
- **View Full** to see in new tab
- **Copy** URLs for sharing

---

## 💡 Tips for Best Results

### Caption Writing
- **Be specific**: "Modern workspace with laptop" > "Nice office"
- **Include mood**: "Inspiring, professional, warm lighting"
- **Mention style**: "Minimalist", "Vibrant", "Cinematic"

### Hashtags
- Use relevant hashtags (#startup, #founder, #design)
- They influence the visual style
- 3-5 hashtags work best

### Format Selection
- **Image**: Quick, single message
- **Carousel**: Step-by-step, lists, stories
- **Video**: Action, process, day-in-life

---

## ⚡ Performance

### Generation Times
- **Single Image**: ~20 seconds
- **Carousel (3 slides)**: ~22 seconds (concurrent)
- **Carousel (5 slides)**: ~25 seconds (concurrent)
- **Video (6 scenes)**: ~25 seconds (concurrent)

### Why So Fast?
- Concurrent generation (multiple images at once)
- Optimized AWS Bedrock calls
- Efficient S3 upload

---

## 🎯 Use Cases

### Social Media Posts
- Instagram feed posts
- LinkedIn articles
- Twitter threads with images

### Marketing Content
- Product announcements
- Feature highlights
- Customer testimonials

### Educational Content
- How-to guides
- Tips and tricks
- Industry insights

### Storytelling
- Founder stories
- Behind-the-scenes
- Company culture

---

## 🔧 Technical Details

### Image Specifications
- **Size**: 1024x1024 pixels
- **Format**: PNG
- **Quality**: High (AWS Bedrock Titan v2)
- **Storage**: AWS S3 with presigned URLs

### URL Expiration
- URLs valid for **7 days**
- Download images for permanent storage
- Re-generate if URLs expire

### Brand Alignment
- Uses your Brand DNA
- Integrates with scraped website content
- Follows your tone and style

---

## ❓ FAQ

### Q: Can I edit the generated images?
A: Download them and edit in your preferred tool (Photoshop, Canva, etc.)

### Q: Can I generate multiple variations?
A: Yes! Click generate again for a new variation

### Q: What if I don't like the result?
A: Try adjusting your caption to be more specific about what you want

### Q: Can I use these commercially?
A: Yes, images generated with AWS Bedrock Titan are yours to use

### Q: How much does it cost?
A: ~$0.008 per image. Very affordable!

### Q: Can I generate without images (prompts only)?
A: Yes, useful for testing. The prompts can guide manual design.

---

## 🐛 Troubleshooting

### "Generation taking too long"
- Normal for carousels/videos (20-30s)
- Check your internet connection
- Try again if it times out

### "No image URL in response"
- AWS credentials may not be configured
- You'll still get prompts to use manually
- Contact admin to set up AWS

### "Image URL not loading"
- URL may have expired (7 days)
- Re-generate the content
- Download images immediately after generation

### "Error generating media"
- Check your caption isn't empty
- Try a different format
- Refresh the page and try again

---

## 📞 Support

### Need Help?
- Check this guide first
- Review error messages
- Try regenerating
- Contact support if issues persist

### Feature Requests?
- We're always improving!
- Share your ideas
- Vote on upcoming features

---

## 🎉 Happy Creating!

The Multi-Modal Creative Studio makes it easy to create professional visual content in seconds. Experiment with different formats and styles to find what works best for your brand!

**Pro Tip**: Generate multiple variations and A/B test to see what resonates with your audience.

---

**Last Updated**: March 2, 2026  
**Version**: 1.0  
**Phase**: 6 Complete ✅
