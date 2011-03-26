<?php

require 'jsonRPCClient.php';

$shaveet = new jsonRPCClient('http://localhost:8082');
switch($_GET['action'])
{
  case 'create_client':
    
    //NOTE:this is not the best way to generate a true random client_id but good enough for demo
    $client_id = $_GET['name'] ."_" . md5(time() . 'S3CR37');
    $key = $shaveet->create_client($client_id);
    $shaveet->subscribe($client_id,'chat-room');
    echo json_encode(array('key' => $key,'client_id' => $client_id));
    break;
  case 'new_message':
    $shaveet->new_message($_GET['client_id'],$_GET['msg'],'chat-room',false);
    echo '1';
    break;
}