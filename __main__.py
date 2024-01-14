from argparse import ArgumentParser
from pathlib import Path

from ipytv import playlist as tv_playlist

# Simple script that takes a m3u file and tries to remove duplicates.
# Example: python3 remove_duplicates.py -i playlist.m3u -o playlist_without_duplicates.m3u
# Example:
# TVP1 HD & TVP1 FHD -> remove TVP1 HD.
# TVP1 FHD & TVP1 HD -> remove TVP1 HD.
# TVP1 4K+ & TVP1 HD -> remove TVP1 HD.
# TVP1 FHD & TVP1 4K+ -> remove TVP1 FHD.

SORTED_QUALITIES = ["4K+", "4K", "FHD", "HD", "SD"]

def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", dest="input", help="Path to m3u+ file", required=True, type=Path)
    parser.add_argument("-v", "--verbose", dest="verbose", help="Verbose output", action="store_true")
    
    return parser.parse_args()

def debug(message: str):
    global verbose
    
    if verbose:
        print("[M3U-LOGO-MATCHER:DEBUG] " + message)
        
def get_channels(playlist: tv_playlist.M3UPlaylist):  
    for channel in playlist:
        yield channel.name

def get_channel_quality(channel_name: str):
    for quality in SORTED_QUALITIES:
        if channel_name.endswith(quality):
            return quality
        
    return None

def truncate_channel_quality(channel_name: str):
    for quality in SORTED_QUALITIES:
        if channel_name.endswith(quality):
            return channel_name[:-len(quality)].strip()
        
    return channel_name

def real_name(channel: tv_playlist.IPTVChannel):
    return channel.name.split(",")[-1]

def find_duplicate_quality(playlist: tv_playlist.M3UPlaylist):
    channels = playlist.get_channels()
    
    for c in channels:
        # Check:
        # example: TVP1 HD & TVP1 FHD -> remove TVP1 HD.
        # example: TVP1 FHD & TVP1 HD -> remove TVP1 HD.
        # example: TVP1 4K+ & TVP1 HD -> remove TVP1 HD.
        
        if any([
            ca for ca in channels 
            if 
                # Check if quality isn't the same
                get_channel_quality(real_name(c)) != 
                get_channel_quality(real_name(ca)) !=
                None
            and
                # Check if channel name is the same
                truncate_channel_quality(real_name(c)) ==
                truncate_channel_quality(real_name(ca))
            and
                # Check if quality is better
                SORTED_QUALITIES.index(get_channel_quality(real_name(c))) <
                SORTED_QUALITIES.index(get_channel_quality(real_name(ca)))
        ]):
            debug(f"Found duplicate quality for {real_name(c)}")
            worse_qualities = get_worse_qualities(
                playlist = playlist, 
                channel = c
            )
            
            if len(worse_qualities) == 0:
                continue
            
            yield c, worse_qualities
            
def get_worse_qualities(playlist: tv_playlist.M3UPlaylist, channel: tv_playlist.IPTVChannel):
    # Example:
    # we assume that channel is TVP1 HD.
    # in playlist we have TVP1 HD, TVP1 FHD, TVP1 4K+.
    # we return TVP1 4K+, because it's the best quality.
    
    sorted_channels = [c for c in playlist 
                       if truncate_channel_quality(real_name(c)) == 
                       truncate_channel_quality(real_name(channel))]
    qualities = []
    
    for quality in SORTED_QUALITIES:
        for c in sorted_channels:
            if c.name.endswith(quality) and \
                SORTED_QUALITIES.index(quality) > \
                SORTED_QUALITIES.index(get_channel_quality(real_name(channel))):
                    
                qualities.append(quality)
    
    return qualities
            
def remove_duplicates(playlist: tv_playlist.M3UPlaylist):
    duplicates = list(find_duplicate_quality(playlist))
    
    print(f"Found {len(duplicates)} duplicates.")
    for duplicate in duplicates:
        c, worse_qualities = duplicate
        debug(f"Preserving {real_name(c)}, because found worse qualities.")
        
        for quality in worse_qualities:
            title_without_quality = truncate_channel_quality(real_name(c))
            
            debug(f"Removing {title_without_quality} {quality}")
            duplicates = [
                channel for channel in playlist 
                if 
                    truncate_channel_quality(real_name(channel)) == 
                    title_without_quality
                and
                    get_channel_quality(real_name(channel)) == 
                    quality
            ]
            
            for duplicate in duplicates:
                index = playlist.get_channels().index(duplicate)
                
                playlist.remove_channel(index)

def process(arguments):
    debug("Processing...")
    playlist = tv_playlist.loadf(str(arguments.input))
    
    remove_duplicates(playlist)
    
    # save playlist
    with open(arguments.input, "w+") as f:
        if arguments.m3u_plus:
            f.write(playlist.to_m3u_plus_playlist())
        else:
            f.write(playlist.to_m3u8_playlist())
        
    print("All done!")
    print("Thanks for using this script!")

if __name__ == "__main__":
    user_choice = input("""
                        
                        WARNING!
                        This script will remove duplicates from your playlist.
                        However, it will OVERWRITE your playlist.
                        
                        We recommend you to make a backup of your playlist.
                        Do you want to continue? [y/n]: """)

    if user_choice.lower() != "y":
        print("Exiting...")
        exit(0)
    
    arguments = parse_arguments()
    verbose = arguments.verbose
    
    process(arguments)