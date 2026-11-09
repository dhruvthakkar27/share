# ============================================================================
# FILE: upload_helper.py
# Enhanced upload manager with threading, timeout, and retry logic
# ============================================================================

import threading
import time
from datetime import datetime
from typing import List, Tuple
import queue


class UploadManager:
    """
    Manages parallel image uploads with timeout protection and status tracking.
    """
    
    def __init__(self, max_upload_time=30, enable_retries=False):
        """
        Initialize upload manager
        
        Args:
            max_upload_time: Maximum time to wait for each upload (seconds)
            enable_retries: If True, retry failed uploads once
        """
        self.max_upload_time = max_upload_time
        self.enable_retries = enable_retries
        self.upload_threads = []
        self.upload_results = queue.Queue()
    
    def upload_async(self, date_str: str, image_type: str, upload_func):
        """
        Start upload in background thread
        
        Args:
            date_str: Date string for organizing images
            image_type: Type of images ("captured_images", "cropped_images", etc.)
            upload_func: Function to call for upload (e.g., send_all_images)
        
        Returns:
            Thread object
        """
        def upload_task():
            start_time = time.time()
            success = False
            error_msg = None
            
            try:
                print(f"[UPLOAD] 📤 Starting upload: {image_type}")
                
                # Call the actual upload function
                upload_func(date_str, image_type)
                
                elapsed = time.time() - start_time
                success = True
                print(f"[UPLOAD] ✓ Upload complete: {image_type} ({elapsed:.1f}s)")
                
            except Exception as e:
                elapsed = time.time() - start_time
                error_msg = str(e)
                print(f"[UPLOAD] ✗ Upload failed: {image_type} - {error_msg} ({elapsed:.1f}s)")
                
                # Retry once if enabled
                if self.enable_retries:
                    try:
                        print(f"[UPLOAD] 🔄 Retrying upload: {image_type}")
                        upload_func(date_str, image_type)
                        success = True
                        print(f"[UPLOAD] ✓ Retry successful: {image_type}")
                    except Exception as retry_error:
                        error_msg = f"Retry failed: {str(retry_error)}"
                        print(f"[UPLOAD] ✗ Retry failed: {image_type} - {error_msg}")
            
            # Store result
            self.upload_results.put({
                'image_type': image_type,
                'success': success,
                'error': error_msg,
                'elapsed': elapsed
            })
        
        # Create daemon thread (won't block program exit)
        thread = threading.Thread(target=upload_task, daemon=True, name=f"Upload-{image_type}")
        thread.start()
        
        # Track thread
        self.upload_threads.append((image_type, thread))
        
        return thread
    
    def wait_for_all(self, timeout_per_upload=None):
        """
        Wait for all uploads to complete
        
        Args:
            timeout_per_upload: Max time to wait for each upload (uses class default if None)
        
        Returns:
            Dictionary with upload statistics
        """
        if timeout_per_upload is None:
            timeout_per_upload = self.max_upload_time
        
        print("\n" + "="*60)
        print("UPLOAD STATUS CHECK")
        print("="*60)
        
        stats = {
            'total': len(self.upload_threads),
            'completed': 0,
            'in_progress': 0,
            'timeout': 0,
            'failed': 0
        }
        
        for image_type, thread in self.upload_threads:
            if thread.is_alive():
                print(f"⏳ Waiting for upload: {image_type} (max {timeout_per_upload}s)")
                thread.join(timeout=timeout_per_upload)
                
                if thread.is_alive():
                    print(f"⚠ Upload timeout: {image_type} (still running in background)")
                    stats['timeout'] += 1
                else:
                    stats['completed'] += 1
            else:
                stats['completed'] += 1
        
        # Process results
        while not self.upload_results.empty():
            result = self.upload_results.get()
            if not result['success']:
                stats['failed'] += 1
        
        # Print summary
        print("="*60)
        print(f"Total uploads: {stats['total']}")
        print(f"✓ Completed: {stats['completed']}")
        if stats['timeout'] > 0:
            print(f"⏳ Still running: {stats['timeout']}")
        if stats['failed'] > 0:
            print(f"✗ Failed: {stats['failed']}")
        print("="*60)
        
        return stats
    
    def get_status(self):
        """Get current status of all uploads without waiting"""
        status = []
        for image_type, thread in self.upload_threads:
            status.append({
                'image_type': image_type,
                'is_alive': thread.is_alive(),
                'name': thread.name
            })
        return status


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    from upload_image import send_all_images
    
    # Create upload manager
    uploader = UploadManager(max_upload_time=30, enable_retries=False)
    
    date_str = datetime.now().strftime("%Y%m%d")
    
    # Start parallel uploads
    uploader.upload_async(date_str, "captured_images", send_all_images)
    uploader.upload_async(date_str, "cropped_images", send_all_images)
    uploader.upload_async(date_str, "inference_images", send_all_images)
    
    # Do other work here...
    print("Doing other work while uploads happen in background...")
    time.sleep(2)
    
    # Optional: check status without waiting
    print("\nCurrent status:")
    for status in uploader.get_status():
        state = "uploading..." if status['is_alive'] else "done"
        print(f"  {status['image_type']}: {state}")
    
    # Wait for all to complete (or timeout)
    stats = uploader.wait_for_all(timeout_per_upload=10)


# ============================================================================
# END OF FILE: upload_helper.py
# ============================================================================