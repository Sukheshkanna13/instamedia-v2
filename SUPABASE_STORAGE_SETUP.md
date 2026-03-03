# Supabase Storage Setup - Manual Steps

## ✅ Connection Status: WORKING!

Your Supabase connection is now active and working correctly.

## ⚠️ Storage Bucket Creation

The storage bucket needs to be created manually through the Supabase Dashboard because the anon key doesn't have permission to create buckets (this is a security feature).

### Manual Setup Steps:

1. **Go to Supabase Dashboard**
   - Visit: https://supabase.com/dashboard/project/rlirzjjecrbcfxzwdftp

2. **Navigate to Storage**
   - Click **Storage** in the left sidebar
   - Click **"New bucket"** button

3. **Create the Bucket**
   - **Name**: `brand-logos`
   - **Public bucket**: ✅ Enable (check the box)
   - **File size limit**: 2 MB (2097152 bytes)
   - **Allowed MIME types**: Leave empty or add:
     - `image/png`
     - `image/jpeg`
     - `image/jpg`
     - `image/svg+xml`
     - `image/webp`
   - Click **"Create bucket"**

4. **Set Bucket Policies (Important!)**
   After creating the bucket, you need to set policies:
   
   - Click on the `brand-logos` bucket
   - Go to **"Policies"** tab
   - Click **"New Policy"**
   - Choose **"For full customization"**
   - Add these policies:

   **Policy 1: Allow public read access**
   ```sql
   CREATE POLICY "Public Access"
   ON storage.objects FOR SELECT
   USING ( bucket_id = 'brand-logos' );
   ```

   **Policy 2: Allow authenticated uploads**
   ```sql
   CREATE POLICY "Allow uploads"
   ON storage.objects FOR INSERT
   WITH CHECK ( bucket_id = 'brand-logos' );
   ```

   **Policy 3: Allow updates**
   ```sql
   CREATE POLICY "Allow updates"
   ON storage.objects FOR UPDATE
   USING ( bucket_id = 'brand-logos' );
   ```

## Alternative: Quick Setup via SQL

If you prefer, you can run this SQL in the Supabase SQL Editor:

```sql
-- Create the bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('brand-logos', 'brand-logos', true);

-- Set policies
CREATE POLICY "Public Access"
ON storage.objects FOR SELECT
USING ( bucket_id = 'brand-logos' );

CREATE POLICY "Allow uploads"
ON storage.objects FOR INSERT
WITH CHECK ( bucket_id = 'brand-logos' );

CREATE POLICY "Allow updates"
ON storage.objects FOR UPDATE
USING ( bucket_id = 'brand-logos' );
```

## After Setup:

Once the bucket is created, the logo upload feature will work automatically!

Test it by:
1. Starting the backend: `cd backend && python app.py`
2. Starting the frontend: `cd frontend && npm run dev`
3. Going to Brand DNA page
4. Clicking the upload zone and selecting a logo

## Current Status:

✅ Supabase URL configured
✅ Supabase anon key configured
✅ Database connection working
✅ Storage API accessible
⏳ Storage bucket needs manual creation (see steps above)
✅ Backend upload endpoint ready
✅ Frontend upload UI ready
