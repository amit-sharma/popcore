/*functions.js 
* Main JS file with custom functions
* Contains mostly functions that do not need to be embedded in the html
*
* Amit Sharma
*/


/* 
* Function set for the suggest dialog 
*/
function addFriendSuggestInput($element){
	$element.append('<div class="suggest-friends-block" style="overflow: hidden;">'+
			'<div class="formWrap"><form class="messageForm" action="#">'+
				'<div class="friends ui-helper-clearfix float-left ui-corner-all" style="width:150px">'+
					'<input class="to" type="text" style="width:50px">'+
				'</div>'+
			'</form></div></div>');
	$('<button style="position:absolute; top:0px;right:0px;" class="closeb"></button>')
		.appendTo($element)
		.button({
			icons: {
				primary: 'ui-icon-circle-close'
			},
			text: false
		})
		/*.position({

			my: 'right',

			to: 'right',

			of: $element

		})*/
		.click(function(){
			backToNormalSize($(this).parent());
			return false;
		});
}

function addFriendSuggestButton($element){
	$element.children('.suggest-friends-block:first').prepend('<button class="suggestb float-right">Suggest</button>');
	$element.find('.suggestb')
		.button()
		.click(function(){
			var item_name=$element.children('a:first').text();
			var item_link = $element.children('a:first').attr('href');
			$('#suggest_dialog').data('item_info', {'name':item_name, 'link':item_link, 'caption':""});
			
			var friends = new Array();
			$(this).next().find('.friends > span').each(function(index){
				friends[index] = $(this).attr('id');
			});
			$('#suggest_dialog').data('friends_list', friends);
			
			openSuggestDialog($('#own_items'), $element.children('div:first').children('img:first').attr('src'));
		});
}

function insertFormattedFriend($element, ui) {
	var friend = ui.item.value;
	var span = $("<span>").attr('id', ui.item.id).addClass('ui-state-highlight ui-widget-content ui-corner-all').css('margin','5px').css('padding','2px').text(friend);
	var a = $("<a>").addClass("remove").attr({
		href: "javascript:",
		title: "Remove " + friend
	}).text("x").appendTo(span);

	//add friend to friend div
	span.insertBefore($element);
}

function openSuggestDialog($position_el, image_src) {
	$( "#suggest_dialog" )
		.dialog("option", "position", {
								my: 'center',
								to: 'center',
								of: $position_el
		})
		.dialog( "open" );
	//alert("Dialog");
	var pic_url=image_src; //#log-elemet img
	//$.get('../get_imageshack.php', {img_url: pic_url}, function(resp){$('#ajax_placeholder').attr('src', resp);} );
	return false;
}

/* Can be removed when feel like */
function log( item ) {
	//$( "<div/>" ).text( item?item.label:hoa ).prependTo( "#log" );
	//$( "#log" ).attr( "scrollTop", 0 );
	if (item) {
	    item.page_url = "http://www.facebook.com/profile.php?id=" + item.id;
		//var $suggestb = $('<button>Suggest to</button>');
		$('#log').show();
		$('#log-content').empty()
				.append('<img class="float-left" src="'+item.pic+'"/>')
				.append('<a href="'+item.page_url+'">'+item.label+'</a><br />'+'<span>'+ item.category + '</span>')
				.append('<fb:like href="' + item.page_url + '" show_faces="true" width="200" layout="button_count" font=""></fb:like>');
				//.append($suggestb);
		//alert("Log called");
		//$suggestb.click(streamPublish)
			
	
	} else {
		$('#log').append("Nothing found!");
	}
}







/*
function callAJAXSearch() {
		$.get('get_search.php', { query: $('#searchbox').attr('value') }, function(data) {
			$('#searchresult').html(data);
			// create the facebook buttons
			FB.XFBML.parse();
			activateToolTips();
			//Stars
			$("#stars-wrapper2").stars({
				inputType: "select"
			});
	});
}
*/

function getAjaxReccos(returned_html, uid){
	var $recco = $('#recco');
	$recco
		.removeClass('ajax-loading')
		.html(returned_html);
	
	$recco.find('a').attr('target', '_blank');
	// create the facebook buttons
	FB.XFBML.parse();
	activateToolTips();
	
	
	$recco.find('button.cancelb').button({
		icons: {
			primary: 'ui-icon-redcancel'
		},
		text: false
	});
	$recco.find('button.cancelb').click(function(){
		var item_id = $(this).parent().attr('id');
		
		$.ajax({
			url: "../record_user_feedback.php", 
			data: {'action': 'not_interested', 'item_id': item_id, 'uid': uid},
			cache: false
		});
	});
	
	$recco.find('button.cancelb').each(function() {
			$(this).qtip({
				content: {
					text: "Thanks for rating!"
				},
				show: {
					event: 'click',
					solo: true
				},
				hide: {
					event: 'false',
					inactive: 1000
				},
				position: {
					my:'top right',
					at:'bottom right',
					target: $(this)
				},
				style: {
					tip: {
						corner: true,
						offset: 20
					}
				}
			});
	});
	
	//Stars
	$recco.data("rated_items_count", 0);
	//raty assumes that the start value is given in $(this).attr('name').
	$('.rating-stars').raty({
			path: 'images/ratings/',
			half: true,
			//start: parseFloat($(this).attr('name')),
			click: function(score, evt) {
				var item_id = $(this).parent().attr('id');
				var $star_obj = $(this);
				$star_obj.qtip({
					content: {
						text: "Thanks for rating!"
					},
					show: {
						event: 'click',
						solo: true
					},
					hide: {
						event: 'false',
						inactive: 1000
					},
					position: {
						my:'top left',
						at:'bottom left',
						target: $star_obj
					},
					style: {
						tip: {
							corner: true,
							offset: 10
						}
					}
				});
				
				$.ajax({
					url: "../record_user_feedback.php", 
					data: {'action': 'star', 'item_id': item_id, 'uid': uid, 'rating': score},
					cache: false
				});
				//$.get('rate_item.php', {'item_id': $(this).parent().attr('id'), 'rating': score});
				var rated_count =$("#recco").data("rated_items_count");
				rated_count += 1;
				$("#recco").data("rated_items_count", rated_count);
				if (rated_count >= $(this).parent().parent().children().size()) {
					alert("Thank you for your feedback. Try our other recommendation tabs too!");
				}
			}
	});
	
	//$('.rating-stars').each (function(){ alert($(this).attr('name'));});
	//For the feedback:temporarily disabled
	//$("#user_feedback").show();
}

function activateStreamTicker() {
	$("#stream_ticker").data("stream_counter", 0);
	var recur_fn = function() {
		$("#stream_ticker").fadeOut(1000, function() {
			var index = $("#stream_ticker").data("stream_counter");
			$("#stream_ticker").html($("#stream").children('ul:first').children().eq(index).html());
			$("#stream_ticker").data("stream_counter",index+1);
			$("#stream_ticker").show('highlight',{}, 5000, recur_fn);
		});
	};
	$("#stream_ticker")
		.show('highlight',{}, 5000, recur_fn);
}

function backToNormalSize($el) {
	var position_top= $el.position().top;
	var font_decrease = $el.data('font-decrease');
	$el
		.css('text-align', 'center')
		.css('max-width', '120px')
		.animate({height: $el.data('original-height'), width: $el.data('original-width')}, 1500, "easeOutCubic")
		.children().first().children().last().remove();
	
	var w_others = 0;
	$el.siblings().each(function() {
		if ($(this).data('size_sideeffect')) {
			w_others+=$(this).width()+12;
			$(this).animate({fontSize:'+='+font_decrease+'px'}, 2, "easeOutCubic");
			$(this).data('size_sideeffect', false);
		}
	});
	//alert(w_others+250+12);
	$el.children().last().prev().remove();
	$el.children().last().remove();
	$el.children('div:first').children('span:last').remove();
	//$el.children('a:first').click(function(){$(this).parent().click();return false;});
	
	$el.parent().data('fishEye', false);
	$el.data('fishedOut', false);
}

//TODO: make the activateToolTips only for the content loaded by AJAX
function activateToolTips() {
	$('.items_list > li').each(function(){
		//alert($(this).parent().width());
		if (($(this).parent().width() - $(this).position().left) < 400) {
			my_str = "top right";
			at_str = "bottom left";
		}
		else {
			my_str = "top left";
			at_str = "bottom right";
		}
		
		$(this).qtip(
			{
	      		content:{
	      			text: '<img class="throbber" src="images/throbber.gif" alt="Loading..." />',
	      			ajax: {
	                    url: 'get_tooltip.php',
	                    type: 'GET',
	                    data: {name:$(this).children('a.item-name').first().text()}
	                 },
	                 title: {
	                    text: $(this).children('a.item-name').first().text(), // Give the tooltip a title using each elements text
	                    button: false
	                 }
	      		},
		      	style: {
		      		classes: 'ui-tooltip-rounded ui-tooltip-shadow ui-tooltip-green',
		      		widget: false
		      	},
		      	position: {
	      		     my: my_str,
	      		     at: at_str,
	      		     target: $(this)
	      		}
	      	});
	});
}


function invite(){
    FB.ui({ method: 'apprequests',
    message: 'Check out Pop Core!'});
   	return false;
}

function streamPublish(){
	//$item_info = $('#log').children().first();
    FB.ui(
    {
        method: 'feed',
        name: 'Pop Core',
        link: 'http://apps.facebook.com/popcore',
        //picture: 'http://4.bp.blogspot.com/_Q8wwMOlEpyc/TRSR97W-KpI/AAAAAAAAACY/XcG0fJk5WXE/s1600/blackswan.jpg',
        caption: 'Books.Movies.Culture.You. And more!',
        description: '',
        message: 'What do you want to explore today?'
    },
    function(response) {
    	if (response && response.post_id) {
    	      alert('Post was published.');
    	} else {
    	      alert('Post was not published.');
    	}
    });
}


function updateTips( t ) {
	var tips = $( ".validateTips" );
	tips
		.text( t )
		.addClass( "ui-state-highlight" );
	setTimeout(function() {
		tips.removeClass( "ui-state-highlight", 1500 );
	}, 500 );
}

function checkLength( o, n, min, max ) {
	if ( o.val().length > max || o.val().length < min ) {
		o.addClass( "ui-state-error" );
		updateTips( "We encourage you to share a personal message too!");
		return false;
	} else {
		return true;
	}
}

function handleAjaxError(x,e){
	if(x.status==0){
		alert('Whoops, error! \n Please reload the page.');
	}else if(x.status==404){
		alert('Requested URL not found.');
	}else if(x.status==500){
		alert('Whoops, Internal Error! \n Please reload the page.');
	}else if(e=='parsererror'){
		alert('Error.\nParsing JSON Request failed.' + x.responseText);
	}else if(e=='timeout'){
		alert('Request Time out.');
	}else {
		alert('Unknown Error.\n'+x.responseText);
	}
}

var dynamicClickHandler = function(e) {
							if ($(this).parent().data('fishedOut') === true){
								window.open($(this).attr('href'));
								return true;
							} else {
								$(this).parent().click(); 
								return false;
							}
						};
/*
function easeOutAnimate(){
	$(this)
		.css('text-align', 'left')
	//	.animate({height: "hide", width: "hide"}, 1500, "easeOutCubic")
		.animate({height: '+=50' , width: '+=50'}, 1500, "easeOutCubic", function() {
			$(this).append('<div id="suggest-input" style="width: 200px; overflow: hidden;">'+
					'<button id="suggestb" class="float-right">Suggest To</button>'+
					'<div id="formWrap"><form id="messageForm" action="#">'+
						'<div id="friends" class="ui-helper-clearfix float-left ui-corner-all" style="width:120px">'+
							'<input id="to" type="text">'+
						'</div>'+
					'</form></div></div>')
		});
	$(this).children().first().append("Movie you see!");
}
*/
function sendAJAXCloseEvent() {
	$.ajax({
	    cache: false,
	    async: false,
        url: "../record_app_close.php"
	    });
	//alert("Hi");
	//$.get("../record_app_close.php");
}
