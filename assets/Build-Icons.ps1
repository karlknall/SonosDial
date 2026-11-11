$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$assetRoot=$PSScriptRoot
New-Item -ItemType Directory -Force -Path $assetRoot | Out-Null
$svg=@'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="SonosDial rotary knob and sound waves">
 <rect width="512" height="512" rx="108" fill="#151719"/>
 <circle cx="216" cy="256" r="126" fill="none" stroke="#f8faf9" stroke-width="24"/>
 <path d="M250 222L288 184" stroke="#60dac6" stroke-width="28" stroke-linecap="round"/>
 <path d="M380 218Q410 256 380 294M420 183Q476 256 420 329" fill="none" stroke="#60dac6" stroke-width="18" stroke-linecap="round"/>
</svg>
'@
[IO.File]::WriteAllText((Join-Path $assetRoot 'sonosdial.svg'),$svg,[Text.UTF8Encoding]::new($false))
$frames=@()
foreach($iconSize in @(16,24,32,48,64,128,256,512)){
 $bitmap=[Drawing.Bitmap]::new($iconSize,$iconSize)
 $g=[Drawing.Graphics]::FromImage($bitmap)
 $g.SmoothingMode=[Drawing.Drawing2D.SmoothingMode]::AntiAlias
 $g.ScaleTransform($iconSize/512.0,$iconSize/512.0)
 $background=[Drawing.SolidBrush]::new([Drawing.ColorTranslator]::FromHtml('#151719'))
 $outline=[Drawing.Pen]::new([Drawing.ColorTranslator]::FromHtml('#f8faf9'),24)
 $accent=[Drawing.Pen]::new([Drawing.ColorTranslator]::FromHtml('#60dac6'),28)
 $accent.StartCap=$accent.EndCap=[Drawing.Drawing2D.LineCap]::Round
 $waves=[Drawing.Pen]::new($accent.Color,18);$waves.StartCap=$waves.EndCap=[Drawing.Drawing2D.LineCap]::Round
 $path=[Drawing.Drawing2D.GraphicsPath]::new()
 $path.AddArc(0,0,216,216,180,90);$path.AddArc(296,0,216,216,270,90)
 $path.AddArc(296,296,216,216,0,90);$path.AddArc(0,296,216,216,90,90);$path.CloseFigure()
 $g.FillPath($background,$path)
 $g.DrawEllipse($outline,90,130,252,252)
 $g.DrawLine($accent,250,222,288,184)
 $g.DrawBezier($waves,[Drawing.PointF]::new(380,218),[Drawing.PointF]::new(400,243.33),[Drawing.PointF]::new(400,268.67),[Drawing.PointF]::new(380,294))
 $g.DrawBezier($waves,[Drawing.PointF]::new(420,183),[Drawing.PointF]::new(457.33,231.67),[Drawing.PointF]::new(457.33,280.33),[Drawing.PointF]::new(420,329))
 $png=Join-Path $assetRoot "sonosdial-$iconSize.png"
 $bitmap.Save($png,[Drawing.Imaging.ImageFormat]::Png)
 if($iconSize -le 256){$frames+=,[IO.File]::ReadAllBytes($png)}
 $g.Dispose();$bitmap.Dispose();$background.Dispose();$outline.Dispose();$accent.Dispose();$waves.Dispose();$path.Dispose()
}
$stream=[IO.File]::Create((Join-Path $assetRoot 'sonosdial.ico'))
$writer=[IO.BinaryWriter]::new($stream)
$writer.Write([uint16]0);$writer.Write([uint16]1);$writer.Write([uint16]$frames.Count)
$offset=6+16*$frames.Count
$sizes=@(16,24,32,48,64,128,256)
for($i=0;$i -lt $frames.Count;$i++){
 $dimension=if($sizes[$i] -eq 256){0}else{$sizes[$i]}
 $writer.Write([byte]$dimension);$writer.Write([byte]$dimension);$writer.Write([byte]0);$writer.Write([byte]0)
 $writer.Write([uint16]1);$writer.Write([uint16]32);$writer.Write([uint32]$frames[$i].Length);$writer.Write([uint32]$offset)
 $offset+=$frames[$i].Length
}
foreach($frame in $frames){$writer.Write([byte[]]$frame)}
$writer.Dispose();$stream.Dispose()
$small=[Drawing.Bitmap]::new(55,55)
$graphics=[Drawing.Graphics]::FromImage($small);$graphics.Clear([Drawing.Color]::White)
$image=[Drawing.Image]::FromFile((Join-Path $assetRoot 'sonosdial-64.png'))
$graphics.DrawImage($image,3,3,49,49);$small.Save((Join-Path $assetRoot 'installer-small.bmp'),[Drawing.Imaging.ImageFormat]::Bmp)
$image.Dispose();$graphics.Dispose();$small.Dispose()
Write-Output 'Created original SVG, PNG and multi-resolution Windows ICO assets'
