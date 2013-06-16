<?php
require_once('config.php');
require_once('lib/lens_lib.php');

//Workaround for IE
if (stristr($_SERVER['HTTP_USER_AGENT'], 'MSIE'))
	header('p3p: CP="ALL DSP COR PSAa PSDa OUR NOR ONL UNI COM NAV"');

//PHP session start
session_start();

// We may or may not have this data based on a $_GET or $_COOKIE based session.
//
// If we get a session here, it means we found a correctly signed session using
// the Application Secret only Facebook and the Application know. We dont know
// if it is still valid until we make an API call using the session. A session
// can become invalid if it has already expired (should not be getting the
// session back in this case) or if the user logged out of Facebook.
$session = $facebook->getSession();
if (!$session) {
    echo "<script type='text/javascript'>top.location.href = '$loginUrl';</script>";
    exit;
}
//Database Connection
$con = mysql_connect($DB_ADDRESS,$DB_USER,$DB_PASS);
if (!$con) {
	die('Could not connect: ' . mysql_error());
}
mysql_select_db("aagns9c3_humanlens", $con);


$me = null;
$me_friends = null;
$newuser_flag = False;
$user_in_db = True;
// Session based API call.
if ($session) {
  //Checking if the user is already in the database. Also, checking if this is the first time user is using the app.
  try {
    $uid = $facebook->getUser();
    $user_q ="SELECT uid AS 'id', first_name, last_name, gender, has_allowed, updated_time, realtime_changes from users WHERE uid='".$uid."'";
    $res = mysql_query($user_q);
    $me = mysql_fetch_assoc($res);
     
  	if(!$me) {
  		$user_in_db = False;
    }
    
    if (!$me || $me['has_allowed'] == 0) {
    	$me = $facebook->api('/me');
    	$newuser_flag = True;
    }
    
    $me_user=new User($me);
    //$friend_movies=$facebook->api('/sethi.san/movies');
  } catch (FacebookApiException $e) {
    error_log($e);
  }
}

//Populate the session table to have a history of all logins
$s_query = "INSERT INTO session_info VALUES('".session_id()."','".$session['sig']."','".$uid."','".date("Y-m-d H:i:s")."', NULL)";
mysql_query($s_query);

//The following code assumes friends, movies for the user are updated through real-time api
//TODO Add larger pics so that can resize! change across everywhere
//$checkquery="SELECT * FROM users WHERE uid='".$me_user->id."'";
//if (mysql_num_rows(mysql_query($checkquery)) == 0) {
if ($newuser_flag) {
	if ($user_in_db) {
		$query="UPDATE users SET gender=".$me_user->gender.", has_allowed=1, updated_time=NOW(), realtime_changes=NULL, algo_order='".serialize($algos_arr)."' WHERE uid='".$me_user->id."' LIMIT 1";
	} else {
		$query="INSERT INTO users VALUES('".$me_user->id."','".$me_user->firstname."','".$me_user->lastname."',".$me_user->gender.",1,NOW(),NULL,'".serialize($algos_arr)."')";
	}
	$insert_flag=mysql_query($query);
	
	//TODO IMP optimize the queries execution, do not ask for all the queries together
	try {
		$queries = array(
			array('method'=>'GET', 'relative_url'=>'/me/movies'),
			array('method'=>'GET', 'relative_url'=>'/me/books'),
			array('method'=>'GET', 'relative_url'=>'/me/television'),
			array('method'=>'GET', 'relative_url'=>'/me/friends')
		);
		$batch_request = $facebook->api('/?batch='.json_encode($queries), 'POST');
		$me_movies=json_decode($batch_request[0]['body'], True);
		$me_books=json_decode($batch_request[1]['body'], True);
		$me_television=json_decode($batch_request[2]['body'], True);
		$me_friends=json_decode($batch_request[3]['body'], True);
		
		
		//get picture and page url from FQL table page
		$page_ids=array();
		foreach(array_merge($me_movies['data'], $me_books['data'], $me_television['data']) as $item){
			$page_ids[] = $item['id'];
		}
		$fql = "SELECT page_id, pic_small, page_url FROM page WHERE page_id IN (".implode(',', $page_ids).")";
		$page_results = $facebook->api(array(
			'method' => 'fql.query',
			'query' =>$fql,
		));
		
		//unoptimized function, but not nec now
		$page_ids = array();
		foreach($page_results as $key=>$item) {
			$page_ids[$key] = $item['page_id']; 
		}
		array_join_on_param($me_movies['data'], $page_results, $page_ids, "id", "page_id");
		array_join_on_param($me_books['data'], $page_results, $page_ids, "id", "page_id");
		array_join_on_param($me_television['data'], $page_results, $page_ids, "id", "page_id");
	} catch (FacebookApiException $e) {
		echo "Error in Facebook API Call".$e;
    	error_log($e);
  	}
  	
  	$me_user->movies = $me_movies['data'];
  	$me_user->books= $me_books['data'];
  	$me_user->television=$me_television['data'];
  	//echo json_last_error();
  	//Database takes care of duplicates
  	//echo '<pre>';var_dump($me_user->books);echo '</pre>';
  	//$me_user->insertFriends();
  	$me_user->insertItems();

  	//Breaking up name into firstname and lastname for all friends
  	for($j=0; $j < count($me_friends['data']); $j++) {
  		$name_array=explode(" ", $me_friends['data'][$j]['name'], 2);
  		$me_friends['data'][$j]['first_name'] = $name_array[0];
  		$me_friends['data'][$j]['last_name'] = $name_array[1];
  	}
  	
  	foreach ($me_friends['data'] as $friend) {
  		$me_user->insertFriend($friend);
  	}
  	
  	//update timestamp to denote when the user details were last edited
	$me_user->updateTimeStamp();
	
} else {
	if (!empty($me['realtime_changes'])){
		try { 
			$changes_str= $me['realtime_changes'];
			$changes_arr = explode(",", $changes_str);
			array_shift($changes_arr);
			$graph_q = array();
			foreach($changes_arr as $changed_field){
				$graph_q[] = array('method'=>'GET', 'relative_url'=>'/me/'.$changed_field);
			}
			$batch_request = $facebook->api('/?batch='.json_encode($graph_q), 'POST');
			for($k = 0; $k <count($batch_request);$k++){
				$me_items[$changes_arr[$k]]= json_decode($batch_request[$k]['body'], True);
			}
			
			//TODO IMP sort by time, and then compare, make it nlogn
			$me_cat_ret_arr=array();
			foreach($changes_arr as $ch_str){
				$me_cat_ret_arr[] = getCategory_GraphAPI($ch_str);
			}
			$like_q="SELECT item_id FROM user_likes, items WHERE uid='".$uid."' AND item_id=id AND category IN (".implode(",",$me_cat_ret_arr).")";
			//echo $like_q;
			$like_res = mysql_query($like_q);
			$db_profile_items=array();
			while($row=mysql_fetch_assoc($like_res)){
				$db_profile_items[] = $row['item_id'];
			}
			
			$add_page_ids=array();
			$added_items=array();
			$deleted_items=array();
			$me_item_ids=array();
			//cat stands for category
			foreach($me_items as $me_cat_items) {
				foreach($me_cat_items['data'] as $item){
					//$date_arr=explode("T", $item['created_time'], 2);
					//if ($db_updated_date <= $date_arr[0]) {
					if (array_search($item['id'], $db_profile_items) === False){
						$add_page_ids[] = $item['id'];
						$added_items[] = $item;
					}
					$me_item_ids[] = $item['id'];
				}
			}
			
			//For handling deletion of items from profile
			foreach($db_profile_items as $item_id){
					if (array_search($item_id, $me_item_ids) === False) {
						$deleted_items[] = $item_id;
						$del_q = "DELETE FROM user_likes WHERE uid='".$uid."' AND item_id='".$item_id."'";
						//echo $del_q."<br/>";
						mysql_query($del_q);
					}
			}
			//var_dump($added_items);
			//var_dump($db_profile_items);
			$fql = "SELECT page_id, pic_small, page_url,type FROM page WHERE page_id IN (".implode(',', $add_page_ids).")";
			$page_results = $facebook->api(array(
				'method' => 'fql.query',
				'query' =>$fql,
			));
			
			//unoptimized function, but not nec now to optimize
			//TODO optimize
			$page_ids = array();
			foreach($page_results as $key=>&$item) {
				$page_ids[$key] = $item['page_id']; 
				//to add field uid, so that can add to user_likes table in db
				$item['uid']=$uid;
			}
			
			
			array_join_on_param($added_items, $page_results, $page_ids, "id", "page_id");
			//var_dump($added_items);
			insertItemDetails($added_items);
			insertUserLikesAndUpdateTimestamp($added_items);
			
			//TODO IMP also update friends, also what to do if number of likes decreases
			
			
			//Restoring it back to NULL
			$update_q = "UPDATE users SET realtime_changes=NULL WHERE uid='".$uid."'";
			mysql_query($update_q);
		} catch (FacebookApiException $e) {
			echo "Error in Facebook API Call".$e;
    		error_log($e);
  		}
	}
	$me_user->fetchItemsFromDatabase();
	
	$friendsq="SELECT uid AS id, first_name, last_name FROM users WHERE uid IN (SELECT uid1 from user_friends WHERE uid2='".$me_user->id."' UNION SELECT uid2 from user_friends WHERE uid1='".$me_user->id."')";
	$result=mysql_query($friendsq);
	$me_friends=array();
	$me_friends['data']=array();
	while ($row = mysql_fetch_assoc($result)) {
		$me_friends['data'][] = $row;
	} 
}

//Converting friend data to friend objects
foreach ($me_friends['data'] as $friend) {
	$me_user->friends[$friend['id']] = new User($friend, False);
}

if(!isset($_SESSION['user_object'])) {
	$_SESSION['user_object'] = serialize($me_user);
}

mysql_close($con);
?>

<!doctype html>
<html lang=en xmlns:fb="http://www.facebook.com/2008/fbml">
	<head>
		<meta charset=UTF-8>
    	<title>Pop Core</title>
		<!--[if lt IE 9]><script src=http://html5shiv.googlecode.com/svn/trunk/html5.js></script><![endif]-->
    	<link type="text/css" href="css/trontastic/jquery-ui.custom.css" rel="stylesheet" />
    	<link type="text/css" href="css/styles.css" rel="stylesheet" />
    	<link type="text/css" href="css/jquery.qtip.css" rel="stylesheet" />
	</head>
	<body>
    <!--
      We use the JS SDK to provide a richer user experience. For more info,
      look here: http://github.com/facebook/connect-js
    -->
    <div id="fb-root"></div>
    <script>
      window.fbAsyncInit = function() {
        FB.init({
          appId   : '<?php echo $facebook->getAppId(); ?>',
          session : <?php echo json_encode($session); ?>, // don't refetch the session when PHP already has it
          status  : true, // check login status
          cookie  : true, // enable cookies to allow the server to access the session
          xfbml   : true // parse XFBML
        });

		//resizing and removing the ugly scroll bars
		FB.Canvas.setAutoResize();

		/* All the events registered */
	    FB.Event.subscribe('auth.login', function(response) {
	         // do something with response
	         alert("Logged in");
	     	 // whenever the user logs in, we refresh the page
	         //window.location.reload();
	    });
	    FB.Event.subscribe('auth.logout', function(response) {
	         // do something with response
	     	sendAJAXCloseEvent();
	    });

	 	FB.Event.subscribe('edge.create', function(href, widget){
		 	//alert("You liked "+ href);
		 	//console.log(widget);
			var item_id = $(widget['dom']).parent().attr('id');
			$.ajax({
				url: "record_user_feedback.php", 
				data: {'action': 'like', 'item_id': item_id, 'uid':<?php echo $uid;?>},
				cache: false
			});
			
	 	});

	 	FB.Event.subscribe('edge.remove', function(href, widget){
		 	//alert("You unliked "+ href);
		 	var item_id = $(widget['dom']).parent().attr('id');
			$.ajax({
				url: "record_user_feedback.php", 
				data: {'action': 'unlike', 'item_id': item_id, 'uid':<?php echo $uid;?>},
				cache: false
			});
	 	});
	 	
	     /*FB.getLoginStatus(function(response) {
	         if (response.session) {
	             // logged in and connected user, someone you know
	             //login();
	         }
	     });*/
      };

      (function() {
        var e = document.createElement('script');
        e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
        e.async = true;
        document.getElementById('fb-root').appendChild(e);
      }());
    </script>
	
	<div id="supercontainer">
		<div id="topcontainer">A</div>
			<div id="eq">
				<span>88</span>
				<span>77</span>
				<span>55</span>
			</div>
		<div id="middlecontainer">B</div>
		<div id="bottomcontainer">C</div>
	</div>
	
	<script type="text/javascript" src="js/jquery.min.js"></script>
	<script type="text/javascript" src="js/jquery-ui.min.js"></script>
	<script type="text/javascript" src="js/jquery.raty.js"></script>
	<script type="text/javascript" src="js/jquery.qtip.pack.js"></script>
	<script type="text/javascript" src="js/functions.js"></script>
	<script type="text/javascript">
	$(document).ready(function() {
		$( "#items_eq > span" ).each(function() {
			// read initial values from markup and remove that
			var value = parseInt( $( this ).text(), 10 );
			$( this ).empty().slider({
				value: value,
				range: "min",
				animate: true,
				orientation: "vertical"
			});
		});
	});
	</script>
  </body>
</html>
