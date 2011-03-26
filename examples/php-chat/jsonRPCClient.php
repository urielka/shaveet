<?php
/*
					COPYRIGHT

Copyright 2007 Sergio Vaccaro <sergio@inservibile.org>

This file is part of JSON-RPC PHP.

JSON-RPC PHP is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

JSON-RPC PHP is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with JSON-RPC PHP; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/

class HttpWrapper_CURL {
	function post($URL, $data, $referrer="") {         
		 // parsing the given URL
		 $URL_Info=parse_url($URL);

		 // Building referrer
		 if($referrer=="") // if not given use this script as referrer
			 $referrer=$_SERVER["REQUEST_URI"];

		 $ch = curl_init();
		 if(!isset($URL_Info["port"]))
		  $port = 80;
		 else
		  $port = $URL_Info["port"];
		  
		 if(!isset($URL_Info["path"])) {
		  $URL_Info["path"] = "";
		 }
		  
		 curl_setopt($ch, CURLOPT_URL, $URL_Info["host"].":".$port.$URL_Info["path"]);
		 curl_setopt($ch, CURLOPT_HEADER, 0);		// Don't return headers
		 curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);	// Return the result when curl_exec is called
		 curl_setopt($ch, CURLOPT_REFERER, $referrer );	// The referrer
		 curl_setopt($ch, CURLOPT_POST, 1);	// We're doing a post call
		 curl_setopt($ch, CURLOPT_POSTFIELDS, $data);	// Here's the post data
		 $result=curl_exec ($ch);
		 curl_close ($ch);
		 return $result;
	}
}



/**
 * The object of this class are generic jsonRPC 1.0 clients
 * http://json-rpc.org/wiki/specification
 *
 * @author sergio <jsonrpcphp@inservibile.org>
 */
class jsonRPCClient {
  static $numRequests = 0;
  static $timeRequets = 0;
	/**
	 * The server URL
	 *
	 * @var string
	 */
	private $url;
	/**
	 * The request id
	 *
	 * @var integer
	 */
	private $id;
	/**
	 * If true, notifications are performed instead of requests
	 *
	 * @var boolean
	 */
	private $notification = false;
	
	/**
	 * Takes the connection parameters
	 *
	 * @param string $url
	 * @param boolean $debug
	 */
	public function __construct($url) {
		// server URL
		$this->url = $url;
		// message id
		$this->id = 1;
	}
	
	/**
	 * Sets the notification state of the object. In this state, notifications are performed, instead of requests.
	 *
	 * @param boolean $notification
	 */
	public function setRPCNotification($notification) {
		empty($notification) ?
							$this->notification = false
							:
							$this->notification = true;
	}
	
	/**
	 * Performs a jsonRCP request and gets the results as an array
	 *
	 * @param string $method
	 * @param array $params
	 * @return array
	 */
	public function __call($method,$params) {
		$start = microtime(true);
		// check
		if (!is_scalar($method)) {
			throw new Exception('Method name has no scalar value');
		}
		
		// check
		if (is_array($params)) {
			// no keys
			$params = array_values($params);
		} else {
			throw new Exception('Params must be given as array');
		}
		
		// sets notification or request task
		if ($this->notification) {
			$currentId = NULL;
		} else {
			$currentId = $this->id;
		}
		
		// prepares the request
		$request = array(
						'method' => $method,
						'params' => $params,
						'id' => $currentId
						);
		$request = json_encode($request);
		$http = new HttpWrapper_CURL();
		$response = json_decode($http->post($this->url,$request),true);
		self::$timeRequets += (microtime(true) - $start);
    self::$numRequests++;
		// final checks and return
		if (!$this->notification) {
			// check
			if ($response['id'] != $currentId) {

				throw new Exception('Incorrect response id (request id: '.$currentId.', response id: '.$response['id'].')');
			}
			if (array_key_exists('error',$response) && !is_null($response['error'])) {
				throw new Exception('Request error: '.var_dump($response['error']));
			}
			
			return $response['result'];
			
		} else {
			return true;
		}
	}
}
?>