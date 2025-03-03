#!/usr/bin/env python3

# -----------------------------------------------------------------------------
# © pookah, 2023-2025. All Rights Reserved.
#
# This software is proprietary and confidential. Unauthorized copying, sharing,
# or distribution of this software, via any medium, is strictly prohibited
# without express permission from the author (pookah).
#
# Licensed to end user for review purposes only. This license
# does not convey any rights to reproduce, distribute, or create derivative
# works of this software. You may not decompile, reverse engineer, disassemble,
# modify, or otherwise attempt to derive the source code of this software.
#
# DISCLAIMER: This software is provided "AS IS," without any warranties,
# express or implied, including but not limited to the implied warranties
# of merchantability, fitness for a particular purpose, or non-infringement.
# In no event shall the author be liable for any claim, damages, or other
# liability, whether in an action of contract, tort, or otherwise, arising
# from, out of, or in connection with the software or the use of the software.
# -----------------------------------------------------------------------------

import os
import time
import argparse
import shutil
from itertools import chain

import requests
import pandas as pd
import wget


class DownloadBot:
    def __init__(self, api_key=None, downloads_base_dir=None, verbose=False):
        self.api_key = api_key or os.getenv("LEONARDO_API_KEY")
        self.downloads_base_dir = downloads_base_dir or os.getenv("LEONARDO_DOWNLOAD_DIR", os.getcwd())
        self.verbose = verbose
        self.get_user_info()
        os.makedirs(self.download_directory, exist_ok=True)

    def log(self, message):
        if self.verbose:
            print(message)

    def get_user_info(self):
        url = "https://cloud.leonardo.ai/api/rest/v1/me"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            user = response.json()['user_details'][0]['user']
            self.user_id = user['id']
            self.username = user['username']
            self.dataframe_backup_file = os.path.join(self.downloads_base_dir, f"{self.username}_generations.pk")
            self.download_directory = os.path.join(self.downloads_base_dir, f"{self.username}_downloads")
            self.log(f"User Info Retrieved: {self.username} ({self.user_id})")
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving user info: {e}")

    def download_image(self, url, filename, directory=None):
        full_path = directory or self.download_directory
        os.makedirs(full_path, exist_ok=True)
        file_path = os.path.join(full_path, filename)
        if os.path.exists(file_path):
            self.log(f"Already exists: {file_path}")
            return

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            ),
        }
        try:
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            self.log(f"Downloaded with requests: {file_path}")
            return
        except requests.exceptions.RequestException as e:
            self.log(f"Requests download failed for {filename}: {e}. Falling back to wget.")

        try:
            wget.download(url, file_path)
            self.log(f"Downloaded with wget: {file_path}")
        except Exception as e:
            print(f"Error downloading image {filename} with wget: {e}")

    def download_incomplete(self, dataframe):
        if dataframe is None or dataframe.empty:
            self.log("No data available to download.")
            return dataframe

        dataframe.reset_index(drop=True, inplace=True)

        if 'downloaded' not in dataframe.columns:
            dataframe['downloaded'] = False
        else:
            dataframe['downloaded'] = dataframe['downloaded'].astype(bool)

        if 'urls' not in dataframe.columns:
            dataframe['urls'] = [[] for _ in range(len(dataframe))]

        pending_downloads = dataframe.loc[~dataframe['downloaded']].copy()
        if pending_downloads.empty:
            self.log("All images have been downloaded.")
            return dataframe

        images = list(chain.from_iterable(pending_downloads['urls'].dropna()))
        for img in images:
            self.download_image(img['url'], img['filename'], directory=self.download_directory)

        dataframe.loc[pending_downloads.index, 'downloaded'] = True
        dataframe.to_pickle(self.dataframe_backup_file)
        return dataframe

    def get_generations(self, offset, limit, u_user_id=None, u_api_key=None):
        u_api_key = u_api_key or self.api_key
        u_user_id = u_user_id or self.user_id
        url = f"https://cloud.leonardo.ai/api/rest/v1/generations/user/{u_user_id}?offset={offset}&limit={limit}"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {u_api_key}"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            self.log(f"Retrieved {limit} generations from offset {offset}")
            return response.json().get('generations', [])
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving generations: {e}")
            return []

    def get_all_generations(self, dataframe=None, limit=50, u_user_id=None, u_api_key=None):
        u_api_key = u_api_key or self.api_key
        u_user_id = u_user_id or self.user_id
        dataframe = dataframe if dataframe is not None else pd.DataFrame(columns=['id'])
        offset = 0
        df_length = limit
        while df_length == limit:
            try:
                dataframe, df_length = self.store_generation_info(dataframe, offset, limit, u_user_id, u_api_key)
                offset += limit
                self.log(f"Progress: {offset} generations retrieved.")
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(0.06)
        return dataframe

    def get_new(self, rebuild=False):
        if rebuild and os.path.exists(self.dataframe_backup_file):
            backup_path = self.dataframe_backup_file + ".bak"
            shutil.move(self.dataframe_backup_file, backup_path)
            self.log(f"Existing dataframe backed up before rebuild. Backup file created at: {backup_path}")
            if os.path.exists(backup_path):
                self.log("Backup file verified.")
            else:
                self.log("Backup file not found after move!")


        try:
            dataframe = pd.read_pickle(self.dataframe_backup_file)
        except FileNotFoundError:
            dataframe = None
        dataframe = self.get_all_generations(dataframe)
        dataframe = self.download_incomplete(dataframe)

        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_file = self.dataframe_backup_file.replace(".pk", f"_{timestamp}.pk")
        dataframe.to_pickle(checkpoint_file)
        self.log(f"Checkpoint backup saved as: {checkpoint_file}")

        return dataframe

    def store_generation_info(self, dataframe, offset, limit, u_user_id=None, u_api_key=None):
        u_api_key = u_api_key or self.api_key
        u_user_id = u_user_id or self.user_id
        df = pd.DataFrame(self.get_generations(offset, limit, u_user_id, u_api_key))
        if 'status' in dataframe.columns:
            dataframe = dataframe[dataframe['status'] != "PENDING"].copy()
        filtered_df = df[~df['id'].isin(dataframe['id'])].copy()
        filtered_df['downloaded'] = False
        if not filtered_df.empty:
            filtered_df['urls'] = filtered_df.apply(self.row_images, axis=1)
            missing_cols = set(dataframe.columns) - set(filtered_df.columns)
            for col in missing_cols:
                filtered_df[col] = None
            dataframe = pd.concat([dataframe, filtered_df], ignore_index=True)
        dataframe.to_pickle(self.dataframe_backup_file)
        self.log(f"Stored {len(filtered_df)} new generations.")
        return dataframe, len(filtered_df)

    def row_images(self, row, completed_only=False):
        images = []
        if row.get('downloaded', False) or not completed_only:
            created_at = row['createdAt']
            for image in row['generated_images']:
                ext = image['url'].split('.')[-1]
                images.append({
                    'url': image['url'],
                    'filename': f"{self.file_compatible_date(row)}_{row['id']}_{image['id']}.{ext}",
                    'created_at': created_at
                })
                for variation in image.get('generated_image_variation_generics', []):
                    images.append({
                        'url': variation['url'],
                        'filename': (
                            f"{self.file_compatible_date(row)}_{row['id']}_{image['id']}_"
                            f"{variation['id']}_{variation['transformType'].lower()}.{ext}"
                        ),
                        'created_at': created_at
                    })
        return images

    def file_compatible_date(self, row):
        return row['createdAt'].replace(":", "-").replace("T", "_")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download generations from Leonardo AI",
        epilog=(
            "Environment Variables:\n\n"
            "  LEONARDO_API_KEY: API key for authentication (overrides --api_key if provided).\n"
            "  LEONARDO_DOWNLOAD_DIR: Base directory for downloads (overrides --download_dir if provided).\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--api_key", type=str, help="API key for authentication", default=None)
    parser.add_argument("--download_dir", type=str, help="Base directory for downloads", default=None)
    parser.add_argument("--rebuild", action="store_true", help="Rebuild dataframe from scratch")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    bot = DownloadBot(api_key=args.api_key, downloads_base_dir=args.download_dir, verbose=args.verbose)
    bot.get_new(rebuild=args.rebuild)
