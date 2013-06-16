<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Amit Sharma</title>

<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
<link rel="shortcut icon" href="favicon.ico" />
<link href="css/style.css" rel="stylesheet" type="text/css" />
<link href="css/rssbox.css" rel="stylesheet" type="text/css" media="all" />
<link href="css/tabstyle.css" rel="stylesheet" type="text/css" media="all" />
<link href="css/galleryview.css" rel="stylesheet" type="text/css" media="all" />
<link href="css/interest_boxes.css" rel="stylesheet" type="text/css" />
<script type="text/javascript" src="javascripts/jquery.js"></script>
<script type="text/javascript" src="javascripts/hovertip.js"></script>
<script type="text/javascript" src="javascripts/jquery.bgpos.js"></script>
<script type="text/javascript" src="javascripts/functions.js"></script>
<!--<script type="text/javascript" src="http://www.google.com/reader/ui/publisher-en.js"></script>
<script type="text/javascript" src="http://www.google.com/reader/ui/publisher-en.js"></script>
<script type="text/javascript" src="http://www.google.com/reader/public/javascript/user/16673305059528282441/label/MyBlog?n=5&callback=GRC_p(%7Bc%3A%22blue%22%2Ct%3A%22My%20Blog%22%2Cs%3A%22false%22%2Cb%3A%22false%22%7D)%3Bnew%20GRC"></script>-->
</head><body>
<div id="wrapper_out">
<div id="wrapper_in">
<div id="maintopPan">
  <div id="maintopPanOne">
    <div id="topHeaderPan">
	  <div id="loadingDiv">&nbsp;Loading...</div>
	  <a href="index2.php" id="myname"><img src="images/mylogo.png" title="Amit Sharma" alt="Amit Sharma" /></a>
      <div class="zoomoutmenu">
        <ul class="zoomtabs">
          <li><a href="#research">Research</a></li>
          <li><a href="#professional">CV</a></li>
          <li><a href="#resources">Resources</a></li>
          <li><a href="#interests">Interests</a></li>
          <li><a href="#aboutme">About Me</a></li>
        </ul>
        <div class="zoompanels">
		  <div id="research" class="zoompanel">
            <h2>Research</h2>
          </div>
          <div id="professional" class="zoompanel">
            <h2>CV</h2>
          </div>
          <div id="resources" class="zoompanel">
            <h2>Resources</h2>
          </div>
		  <div id="interests" class="zoompanel">
            <h2>Interests</h2>
          </div>
          <div id="aboutme" class="zoompanel">
            <h2>About Me</h2>
          </div>
        </div>
      </div>
    </div>
    <div id="topSidemenuPan">
      <ul>
        <li class="home"><a class="sidelinks" href="#home">Home</a></li>
        <li class="contact"><a class="sidelinks" href="#contact">Contact</a></li>
      </ul>
	  <img src="images/home-hover.jpg" style="display:none;" alt="home" />
	  <img src="images/contact-hover2.jpg" style="display:none;" alt="contact"/>
    </div>
  </div>
</div>
<script type="text/javascript">$('.zoomoutmenu').zoomtabs(15);</script>
<div id="bodyPan">
	<div id="leftPan">&nbsp;</div>
	<script type="text/javascript">
		var dochash = window.location.hash;
		if (!dochash)
			$('#leftPan').load("home.html");	
		else 
		{
			$('#leftPan').load(dochash.split('#')[1]+".html");
			if (dochash =="#professional")
				$(".tabs a.tab").bind("click", pullUpTab);
			
		}
	</script>
<?php include "footer.php" ?>
