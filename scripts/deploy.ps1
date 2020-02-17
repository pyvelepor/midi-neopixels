Param(
    [string]$destination,
    [string]$source  
)

$drive = $destination.Split(" ")[1][1];
$source = ".\$($source)";
$destination = "$($drive):\code.py";

Copy-Item $source -Destination $destination;
Get-ChildItem "lib" | ForEach-Object {
    Copy-Item $_.FullName -Destination "$($drive):\lib\." -Recurse -Force
};