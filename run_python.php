<?php
$data = $_POST['data'];
$data = explode(",", $data);
$status = $data[0];
$ranges = $data[1];
 
$command = "python senti_classifier.py";
$command .= " $status $ranges";
 
header('Content-Type: text/html; charset=utf-8');
echo '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />';
echo "<style type='text/css'>
 body{
 background:#000;
 color: #7FFF00;
 font-family:'Lucida Console',sans-serif !important;
 font-size: 12px;
 }
 </style>";
 
$pid = popen( $command,"r");
 
echo "<body><pre>";
while( !feof( $pid ) )
{
 echo fread($pid, 256);
 flush();
 ob_flush();
 echo "<script>window.scrollTo(0,99999);</script>";
 usleep(100000);
}
pclose($pid);
 
echo "</pre><script>window.scrollTo(0,99999);</script>";
echo "<br /><br />Script finalizado<br /><br />";
?>


/*$command = "python senti_classifier.py";
$pid = popen( $command,"r");
while( !feof( $pid ) )
{
 echo fread($pid, 256);
 flush();
 ob_flush();
 //usleep(100000);
}
pclose($pid);*/
 
