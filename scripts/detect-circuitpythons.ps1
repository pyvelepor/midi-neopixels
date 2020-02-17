$CircuitPythons = Get-Disk | 
                  Where-Object {$_.Model -contains "Circuit Playgrou" -and $_.Manufacturer -eq "Adafruit"} |
                  Get-Partition |
                  Get-Volume | 
                  Where-Object DriveType -EQ Removable | 
                  ForEach-Object { 
    $CircuitPython = New-Object -TypeName psobject; 
    $CircuitPython | Add-Member -Type NoteProperty -Name Drive -Value $_.DriveLetter; 
    $CircuitPython | Add-Member -Type NoteProperty -Name Path -Value $_.Path; 
    $CircuitPython | Add-Member -Type NoteProperty -Name Name -Value $_.FileSystemLabel; 
    $CircuitPython;
};

$tasks = Get-Content "tasks-template.json" | ConvertFrom-Json;
$taskinput = ($tasks.inputs | where-object id -eq "circuitpythons")[0];
$taskinput.options = @($CircuitPythons | foreach-object {"$($_.Name) ($($_.Drive):)"});
$taskinput.default = $taskinput.options[0];
$tasks | ConvertTo-Json -depth 100 | Out-File "./.vscode/tasks.json" -Encoding utf8
