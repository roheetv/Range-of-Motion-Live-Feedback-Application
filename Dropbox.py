# Flow of the code — NOT EXECUTABLE

import UI_Framework as ui         # e.g., wx
import Video_IO as vio            # e.g., cv2
import TimeUtils as time
import MathUtils as np
import AngleLib as mp_lib         # your helper module (mediapipe_lib.py)
import ConfigStore as cfg

class VideoFrame(ui.Frame):
    def __init__(self, title, pose_backend):
        super().__init__(title=title, size=(W, H))

        # --- App state ---
        self.pose = pose_backend                  # MediaPipe Pose instance
        self.cap = None                           # video capture (file or webcam)
        self.is_live = False                      # webcam vs file
        self.is_playing = False                   # playback state
        self.is_saving = False                    # export state
        self.out = None                           # writer when exporting
        self.fps = DEFAULT_FPS
        self.progress_dialog = None
        self.angle_colors = cfg.load_colors_or_default(5)  # 5 slots

        # --- Menus / Actions ---
        self.menu_file = self._build_file_menu()          # Browse Video, Live Camera
        self.menu_edit = self._build_color_menu()         # Choose Color for Angle i

        # --- Layout ---
        # Left: angle pickers 
        # Right: video panel + transport controls + slider + save button
        self.video_panel = mp_lib.VideoPanel(parent=self, angle_colors=self.angle_colors)
        self.control_panel = mp_lib.ControlPanel(
            parent=self,
            video_panel=self.video_panel,
            cap=self.cap,
            mp_pose=pose_backend.runtime,   # backend handle(s)
            pose=pose_backend,
            angle_colors=self.angle_colors
        )

        # --- Bind events ---
        # - Angle dropdown changed  → update selected slot in control panel
        # - Reset angle i           → clear selection & reset fixed references
        # - Browse Video            → self.OnBrowseVideo
        # - Live Camera             → self.OnLiveCamera
        # - Play/Pause              → self.OnPlayPause
        # - Prev/Next frame         → self.OnPrevFrame / self.OnNextFrame
        # - Slider moved            → self.OnSliderChange (seek)
        # - Start/Stop Save         → self.OnSaveToggle
        # - Window close            → self.OnClose

        self.show()

    # -------------------------
    # Menu builders (pseudocode)
    # -------------------------
    def _build_file_menu(self):
        # create File menu with “Browse Video”, “Live Camera”
        # bind to handlers
        pass

    def _build_color_menu(self):
        # create Edit menu with “Choose Color for Angle {1..5}”
        # each item opens a system color picker and updates angle_colors
        pass

    # -------------------------
    # Angle selection & colors
    # -------------------------
    def OnAngleSelect(self, event, slot_index):
        selected_label = event.value
        self.control_panel.selected_angles[slot_index] = selected_label
        self.video_panel.Refresh()

    def OnChooseColor(self, event, slot_index_1based):
        new_color = ui.pick_color_dialog()
        cfg.update_color(slot_index_1based - 1, new_color, self.angle_colors)
        self.video_panel.update_angle_colors(self.angle_colors)
        self.control_panel.update_angle_colors(self.angle_colors)

    # -------------------------
    # Video / Camera input
    # -------------------------
    def OnBrowseVideo(self, event):
        path = ui.file_dialog(filters=["*.mp4", "*.mov", "*.avi"])
        if not path: return
        # close previous capture if any
        self._release_capture()
        self.cap = vio.open(path)
        self.is_live = False
        self.control_panel.cap = self.cap
        self._initialize_slider_from_capture(self.cap)
        self.ResetAllAngles()

    def OnLiveCamera(self, event):
        # Open default camera index 0
        self._release_capture()
        self.cap = vio.open_camera(0)
        self.is_live = True
        self.control_panel.cap = self.cap
        self._initialize_slider_for_live()
        self.ResetAllAngles()

    # -------------------------
    # Playback controls
    # -------------------------
    def OnPlayPause(self, event):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.StartPlayback()
        else:
            self.StopPlayback()

    def StartPlayback(self):
        # control_panel’s timer drives frames every ~30 ms
        self.control_panel.timer.start(period_ms=30)

    def StopPlayback(self):
        self.control_panel.timer.stop()

    def OnPrevFrame(self, event):
        # seek one frame back if file input
        if self.cap and not self.is_live:
            current = vio.get_pos(self.cap)
            vio.set_pos(self.cap, max(0, current-1))
            self.control_panel.NextFrame(None)  # render once

    def OnNextFrame(self, event):
        # seek one frame forward if file input
        if self.cap and not self.is_live:
            current = vio.get_pos(self.cap)
            vio.set_pos(self.cap, min(current+1, vio.frame_count(self.cap)-1))
            self.control_panel.NextFrame(None)  # render once

    def OnSliderChange(self, event):
        # when user drags the slider, seek capture and render
        if self.cap and not self.is_live:
            target_frame = event.value
            was_running = self.control_panel.timer.is_running()
            if was_running: self.control_panel.timer.stop()
            vio.set_pos(self.cap, target_frame)
            self.control_panel.NextFrame(None)
            if was_running: self.control_panel.timer.start(30)

    def UpdateSlider(self):
        # keep the UI slider in sync with current frame position
        pass

    def ResetVideo(self):
        if self.cap:
            vio.set_pos(self.cap, 0)
            self.control_panel.video_ended = False

    def ResetAllAngles(self):
        # clear all five dropdowns and reset selected angles & cached references
        for i in range(5):
            # clear UI value
            # clear selection in control panel
            self.control_panel.selected_angles[i] = None
        mp_lib.reset_fixed_coordinates()
        self.video_panel.Refresh()

    # -------------------------
    # Saving / Export 
    # -------------------------
    def OnSaveToggle(self, event):
        if not self.cap or self.is_live:
            ui.alert("Please select a video file first.")
            return
        if self.is_saving:
            self.StopSaving()
        else:
            if self.is_playing:
                self.StopPlayback()
            self.StartSaving()

    def StartSaving(self):
        # Prepare writer with panel size & FPS
        width, height = self.video_panel.get_size()
        self.fps = self._safe_fps_from_cap(self.cap)  # clamp to a sane range
        out_path = self._build_timestamped_output_path()
        self.out = vio.VideoWriter(out_path, fps=self.fps, size=(width, height))
        # progress dialog
        self.progress_dialog = ui.ProgressDialog(title="Saving Video")
        self.is_saving = True
        # spawn a worker thread to iterate frames and request composed frames from panel
        spawn_thread(self.SaveVideoThread)

    def SaveVideoThread(self):
        start = vio.get_pos(self.cap)
        end = vio.frame_count(self.cap)
        for idx in range(start, end):
            if not self.is_saving: break
            ret, frame_bgr = vio.read(self.cap)
            if not ret: break
            # Convert BGR→RGB and run a lightweight render cycle to refresh panel
            # The VideoPanel, when it detects "is_saving", will copy the fully drawn
            # frame (video + overlays) and call back SaveVideoFrames(wx_image)
            self._throttled_progress(idx, end)
            # Sleep minimally to respect target FPS
        # finalize
        if self.is_saving:
            self.UpdateSaveProgress(100)
        self.StopSaving()

    def SaveVideoFrames(self, composed_image_rgb):
        # Convert UI image → numpy BGR and write to file
        if not self.is_saving or not self.out: return
        bgr = convert_rgb_to_bgr(composed_image_rgb)
        self.out.write(bgr)

    def UpdateSaveProgress(self, percent):
        # Update dialog- if user cancels, stop saving
        if self.progress_dialog and self.is_saving:
            keep_going = self.progress_dialog.update(percent)
            if not keep_going:
                self.StopSaving()

    def StopSaving(self):
        # Close writer, hide dialog, notify user
        self.is_saving = False
        if self.out:
            self.out.release()
            self.out = None
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        ui.info("Video saved successfully")

    # -------------------------
    # Cleanup
    # -------------------------
    def OnClose(self, event):
        cfg.save_colors(self.angle_colors)
        self.StopPlayback()
        self._release_capture()
        if self.out: self.out.release()
        self.destroy()

    # -------------------------
    # Helpers 
    # -------------------------
    def _release_capture(self): ...
    def _initialize_slider_from_capture(self, cap): ...
    def _initialize_slider_for_live(self): ...
    def _safe_fps_from_cap(self, cap): ...
    def _build_timestamped_output_path(self): ...
