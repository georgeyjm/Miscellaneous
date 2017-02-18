set rootPath to "/Users/GeorgeYu/Desktop/wallpaper"
repeat
	repeat with imgNum from 1 to 1373
		try
			tell application "Finder" to set desktop picture to POSIX file (rootPath & "-" & imgNum & ".jpg")
		on error
			tell application "Finder" to set desktop picture to POSIX file (rootPath & " - " & imgNum & ".jpg")
		end try
		delay 0.033
	end repeat
end repeat
