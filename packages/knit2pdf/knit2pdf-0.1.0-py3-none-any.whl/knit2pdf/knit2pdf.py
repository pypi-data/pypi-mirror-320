from pydantic import BaseModel
import os
from typing import Optional
import youtube_dl
import whisperx
from .config.knit2pdfoptions import Knit2PDFOptions
from .config.openai import OPENAI_CLIENT

class Knit2PDF(BaseModel):
    youtube_link: str
    youtube_id: str
    video_language: str
    dl_options: Knit2PDFOptions
    transcript: Optional[str] = None
    pattern: Optional[str] = None

    def __init__(self, youtube_link: str, video_language: str, dl_options: Optional[Knit2PDFOptions] = None):
        super().__init__(
            youtube_link=youtube_link,
            youtube_id=youtube_link.split("v=")[1],
            video_language=video_language,
            dl_options=dl_options if dl_options else Knit2PDFOptions()
        )

    def download_video(self) -> None:
        """
        Download the video from the YouTube link.
        """
        if (self.youtube_id+".mp4") not in os.listdir("videos/"):
            with youtube_dl.YoutubeDL(self.dl_options.model_dump()) as ydl:
                ydl.download([self.youtube_link])
                print(f"Downloaded the video from {self.youtube_link} :)")
        else:
            print("Video already downloaded. Skipping download.")
    
    def get_transcript(self) -> str:
        """
        Get the transcript of the video.

        Returns the transcript of the video.
        """

        if (self.youtube_id+".txt") not in os.listdir("transcripts/"):
            # If youtube video doesn't exist, download it
            self.download_video()

            # Get the transcript of the video
            audio_file = f"videos/{self.youtube_id}.mp4"
            batch_size = 8 # reduce if low on GPU mem
            compute_type = "int8" # change to "int8" if low on GPU mem (may reduce accuracy)

            # 1. Transcribe with original whisper (batched)
            model = whisperx.load_model("turbo", device='cpu', compute_type=compute_type, language=self.video_language)
            audio = whisperx.load_audio(audio_file)
            print("Transcribing with Whisper...")
            result = model.transcribe(audio, batch_size=batch_size)
            transcript = "".join([x["text"] for x in result["segments"]])

            # Write transcript to file
            with open(f"transcripts/{self.youtube_id}.txt", "w", encoding="utf-8") as f:
                f.write(transcript)
        else:
            with open(f"transcripts/{self.youtube_id}.txt", "r", encoding="utf-8") as f:
                print("Transcript already exists. Reading from file.")
                transcript = f.read()
        
        self.transcript = transcript
        return transcript
    
    def generate_pattern(self) -> str:
        """
        Get the pattern from the transcript.

        Returns the pattern.
        """
        transcript = self.transcript if self.transcript else self.get_transcript()
        completion = OPENAI_CLIENT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", 
             "content": "You are asked to identify the knit item, and clean up a knitting pattern and extract key instructions to make the knit item."},
            {
                "role": "user",
                "content": "Can you clean the transcription and help to extract key instructions to make the knit item in markdown format? Feel free to modify the pattern that would make the pattern more correct and accurate. \n " + transcript
            }
            ]
    )

        response = completion.choices[0].message.content
        # Clean the response
        if "```" in response:
            arr = response.split("```")
            for p in arr:
                if "#" in p:
                    pattern = p
                    break
        else:
            pattern = response
        
        self.pattern = pattern

        # Write to pattern
        with open(f"patterns/{self.youtube_id}.md", "w", encoding="utf-8") as f:
            print("Writing pattern to file...")
            f.write(pattern)
            print("Pattern written to file.")

        return pattern