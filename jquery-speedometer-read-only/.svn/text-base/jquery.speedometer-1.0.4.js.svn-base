/*

jQuery Speedometer
by Jacob King
http://www.jacob-king.com/

Tested on IE7, IE8, and Firefox 3.6.8 with jQuery 1.4.2
***Requires jquery.jqcanvas-modified.js and excanvas-modified.js***



Usage: 
	$([selector]).speedometer([options object]);

Options:
	percentage: (float/int, default: 0) 
		Value to display on speedometer and digital readout. Can also be specified as the selector's innerHTML.
	scale: (float/int, default: 100)
		The value considered to be 100% on the speedometer. To implement a full-circle speedometer, set this to "50" and the limit to "false"
	offset: (float/int, default: -50)
		The speedometer's orientation. Default of -50 is left. 0 is straight up, 50 is right, and 100 is down. 
			The offset value is proportional to the scale. 
			Example: If the scale is 180, then -90 is left, 0 is straight up, 90 is right, and 180 is down.
	limit: (float/int, default: true)
		Specifies that the speedometer will "break" if the value is out of bounds.
	minimum: (float/int, default: 0)
		The lowest value the needle can go without the glass cracking.
	maximum: (float/int, default: 100)
		The highest value the needle can go without the glass cracking.
	animate: (boolean, default: true)
		Specifies that the speedometer needle will animate from current value to intended value.	
	suffix: (string, default: ' %')
		A unit/string to display after the digital readout's value. Set to an empty string for none.
	
	thisCss: Default settings object for speedometer. Modifying this is not supported.
	
	digitalCss: Default settings object for digital readout. Modifying this is not supported.
	
*/

( function( $ ){

	$.fn.speedometer = function( options ){
	
		/* A tad bit speedier, plus avoids possible confusion with other $(this) references. */
		var $this = $( this );
		

		
		/* handle multiple selectors */
		if ( $this.length > 1 ) {
			$this.each( function(){
				$( this ).speedometer( options );
			});
			return $this;
		}	

		var def = {
			/* If not specified, look in selector's innerHTML before defaulting to zero. */
			percentage : $.trim( $this.html() ) || 0,
			scale: 100,
			offset : -50, //experimental
			limit: true,
			minimum: 0,
			maximum: 100,
			suffix: ' %',
			animate: true,
			thisCss: {
				position: 'relative', /* Very important to align needle with gague. */
				width: '210px',
				height: '180px',
				padding: '0px',
				border: '0px',
				fontFamily: 'Arial',
				fontWeight: '900',
				backgroundImage : "url('./background.jpg')"

		
			},
			digitalCss: {
				backgroundColor:'black',
				borderColor:'#555555 #999999 #999999 #555555',
				borderStyle:'solid',
				borderWidth:'2px',
				color:'white',
				fontSize:'16px',
				height:'20px',
				left:'72px',
				padding:'1px',
				position:'absolute',
				textAlign:'center',
				top:'65px',
				width:'60px',
				zIndex:'10',
				lineHeight:'20px',
				overflow:'hidden'
			}
		}
		

		/* The container needs to be empty. */
		$this.html( '' );
		
		/* Apply CSS rules to container. */
		$this.css( def.thisCss );
		
		/* User-defined settings override default settings. */
		$.extend( def, options );
		
		/* If out of range... */
		if ( def.limit && ( def.percentage > def.maximum || def.percentage < def.minimum ) ) {
			/* ...The glass cracks */
			$this.css( 'backgroundImage' , 'url("./background-broken.jpg")' );
		} else {
		
			




		
			/* Call modified jqcanvas file to generate needle line. */
			$this.jqcanvas ( function ( canvas, width, height ) {
		
				var ctx = canvas.getContext ( "2d" ),
				lingrad, thisWidth;
	
				ctx.lineWidth = 2;
				ctx.strokeStyle = "rgb(255,0,0)";
				
				/* point of origin for drawing AND canvas rotation (lines up with middle of the black circle on the image) */
				ctx.translate( 105,105 );	
							
				ctx.save(); //Remember linewidth, strokestyle, and translate.
				
				function animate(){		
		
					ctx.restore(); //Reset ctx.rotate to properly draw clearRect
					ctx.save();	//Remember this default state again.
		
					ctx.clearRect( -105, -105, 300, 300 ); //Erase the canvas.
		
					
					
		
		
					/* Rotate the canvas, which will orient the needle to position i. */
					ctx.rotate(  ( i + def.offset ) * Math.PI / def.scale );
		
		
		
					/* Draw the needle */
					ctx.beginPath();
					ctx.moveTo( 0, -80);
					ctx.lineTo( 0, 10 );
					ctx.stroke();
					
					/* Internally remember current needle value. */
					$this.data('currentPercentage',i);
					
					
					if ( i != def.percentage ) {
					
						//Properly handle fractions.
						i += Math.abs( def.percentage - i ) < 1 ? def.percentage - i : def.increment;
		
						setTimeout(function(){
							animate()
						},20);
					}
				}				
				
				/* Are we animating or just displaying the percentage? */
				if (def.animate) {
					//Define starting position of needle for animation.
					var i = parseInt( $this.data('currentPercentage') ) || 0;
					
					//Define if movement is clockwise or counter-clockwise.
					def.increment = ( i < def.percentage ) ? 1 : -1; 
				} else {
					var i = ( def.percentage );
				}
				
				
				animate();
				
				
				
			
			}, { verifySize: false, customClassName: '' } );


		
		}
		
		/* digital percentage displayed in middle of image */

		var digitalGauge = $( '<div></div>' );
		$this.append( digitalGauge );
		digitalGauge.css( def.digitalCss );
		digitalGauge.text( def.percentage + def.suffix );
		

		
		return $this;

	}

	

})( jQuery );