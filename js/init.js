/*
	Twenty 1.0 by HTML5 UP
	html5up.net | @n33co
	Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)
*/

skel.init({
	reset: 'full',
	breakpoints: {
		global:		{ range: '*', href: 'css/style.css', containers: 1400, grid: { gutters: 50 } },
		wide:		{ range: '-1680', href: 'css/style-wide.css', containers: 1200, grid: { gutters: 40 } },
		normal:		{ range: '-1280', href: 'css/style-normal.css', containers: 960, lockViewport: true },
		narrow:		{ range: '-980', href: 'css/style-narrow.css', containers: '95%', grid: { gutters: 30 } },
		narrower:	{ range: '-840', href: 'css/style-narrower.css', grid: { collapse: 1 } },
		mobile:		{ range: '-640', href: 'css/style-mobile.css', containers: '100%', grid: { gutters: 15, collapse: 2 } }
	}
}, {
	layers: {

		// Transform test.
			transformTest: function() {

				// Only use CSS transforms with touch devices.
					return (skel.vars.isTouch);

			},

		// Layers.
		// Probably shouldn't mess with these (at least until I've finished the skel-layers documentation).
			layers: {
				topPanel: {
					states: 'global wide normal narrow narrower mobile',
					position: 'top-center',
					side: 'top',
					hidden: true,
					animation: 'pushY',
					width: '100%',
					height: '75%',
					html: '<nav data-action="navList" data-args="nav"></nav>',
					clickToClose: true,
					swipeToClose: false,
					orientation: 'vertical'
				},
				topButton: {
					states: 'global wide normal narrow narrower mobile',
					position: 'top-center',
					width: 120,
					height: 50,
					html: '<span class="toggle" data-action="toggleLayer" data-args="topPanel"></span>'
				},
				sidePanel: {
					states: 'global wide normal narrow narrower',
					position: 'top-left',
					side: 'left',
					hidden: true,
					animation: 'revealX',
					width: 250,
					height: '100%',
					html: '<nav data-action="navList" data-args="nav"></nav>',
					clickToClose: true,
					orientation: 'vertical'
				},
				sideButton: {
					states: 'global wide normal narrow narrower',
					position: 'top-left',
					width: 100,
					height: 60,
					html: '<span class="toggle" data-action="toggleLayer" data-args="sidePanel"></span>'
				}
			}
	}
});

(function($) {

	/* scrolly v0.1 | (c) n33 | n33.co @n33co | MIT */
		(function(e){var t="click.scrolly";e.fn.scrolly=function(r,i){r||(r=1e3),i||(i=0),e(this).off(t).on(t,function(t){var n,s,o,u=e(this),a=u.attr("href");a.charAt(0)=="#"&&a.length>1&&(n=e(a)).length>0&&(s=n.offset().top,u.hasClass("scrolly-centered")?o=s-(e(window).height()-n.outerHeight())/2:(o=Math.max(s,0),i&&(typeof i=="function"?o-=i():o-=i)),t.preventDefault(),e("body,html").stop().animate({scrollTop:o},r,"swing"))})}})(jQuery);

	$(function() {

		var $body = $('body'),
			$window = $(window),
			$header = $('#header'),
			$banner = $('#banner');

		// Re-enable animations until we're done loading everything.
			$window.load(function() {
				$body.removeClass('loading');
			});

		// Placeholder fix (IE<10).
		// If IE<10, use formerize to add support for the "placeholder" attribute.
			if (skel.vars.IEVersion < 10) {

				// formerize v1.0 | (c) n33 | n33.co @n33co | MIT
					$.fn.formerize=function(){var _fakes=new Array(),_form = $(this);_form.find('input[type=text],textarea').each(function() { var e = $(this); if (e.val() == '' || e.val() == e.attr('placeholder')) { e.addClass('formerize-placeholder'); e.val(e.attr('placeholder')); } }).blur(function() { var e = $(this); if (e.attr('name').match(/_fakeformerizefield$/)) return; if (e.val() == '') { e.addClass('formerize-placeholder'); e.val(e.attr('placeholder')); } }).focus(function() { var e = $(this); if (e.attr('name').match(/_fakeformerizefield$/)) return; if (e.val() == e.attr('placeholder')) { e.removeClass('formerize-placeholder'); e.val(''); } }); _form.find('input[type=password]').each(function() { var e = $(this); var x = $($('<div>').append(e.clone()).remove().html().replace(/type="password"/i, 'type="text"').replace(/type=password/i, 'type=text')); if (e.attr('id') != '') x.attr('id', e.attr('id') + '_fakeformerizefield'); if (e.attr('name') != '') x.attr('name', e.attr('name') + '_fakeformerizefield'); x.addClass('formerize-placeholder').val(x.attr('placeholder')).insertAfter(e); if (e.val() == '') e.hide(); else x.hide(); e.blur(function(event) { event.preventDefault(); var e = $(this); var x = e.parent().find('input[name=' + e.attr('name') + '_fakeformerizefield]'); if (e.val() == '') { e.hide(); x.show(); } }); x.focus(function(event) { event.preventDefault(); var x = $(this); var e = x.parent().find('input[name=' + x.attr('name').replace('_fakeformerizefield', '') + ']'); x.hide(); e.show().focus(); }); x.keypress(function(event) { event.preventDefault(); x.val(''); }); });  _form.submit(function() { $(this).find('input[type=text],input[type=password],textarea').each(function(event) { var e = $(this); if (e.attr('name').match(/_fakeformerizefield$/)) e.attr('name', ''); if (e.val() == e.attr('placeholder')) { e.removeClass('formerize-placeholder'); e.val(''); } }); }).bind("reset", function(event) { event.preventDefault(); $(this).find('select').val($('option:first').val()); $(this).find('input,textarea').each(function() { var e = $(this); var x; e.removeClass('formerize-placeholder'); switch (this.type) { case 'submit': case 'reset': break; case 'password': e.val(e.attr('defaultValue')); x = e.parent().find('input[name=' + e.attr('name') + '_fakeformerizefield]'); if (e.val() == '') { e.hide(); x.show(); } else { e.show(); x.hide(); } break; case 'checkbox': case 'radio': e.attr('checked', e.attr('defaultValue')); break; case 'text': case 'textarea': e.val(e.attr('defaultValue')); if (e.val() == '') { e.addClass('formerize-placeholder'); e.val(e.attr('placeholder')); } break; default: e.val(e.attr('defaultValue')); break; } }); window.setTimeout(function() { for (x in _fakes) _fakes[x].trigger('formerize_sync'); }, 10); }); return _form; };

				// Apply formerize all forms.
					$('form').formerize();

			}

		// Scrolly links.
			$('.scrolly').scrolly(1000, -10);

		// Dropdowns.
			$('#nav > ul').dropotron({
				offsetY: -13,
				mode: 'fade',
				noOpenerFade: true,
				expandMode: (skel.vars.isTouch ? 'click' : 'hover')
			});

		// Header.
		// If the header is using "alt" styling and #banner is present, use scrollwatch
		// to revert it back to normal styling once the user scrolls past the banner.
		// Note: This is disabled on touch devices and whenever the 'normal' breakpoint is
		// active (effectively disabling it on 'narrow', 'narrower', and 'mobile' as well).
			if (!skel.vars.isTouch
			&&	$header.hasClass('alt')
			&&	$banner.length > 0) {

				$window.on('load', function() {

					// scrollgress v0.2 | (c) n33 | n33.co @n33co | MIT
						(function(){var e="scrollwatch",t="length",n="top",r=null,i="scrollgress",s="data",o="scrollwatch-state",u="range",a="anchor",f="unscrollwatch",l="unscrollgress",c="removeData",h="element",p="-id",d="scroll.",v="height",m="scrollTop",g="center",y="bottom",b=$(window),w=$(document),E=1e3;$.fn[e]=function(f){var l,c,h,p;if(this[t]>1){for(l=0;l<this[t];l++)$(this[l])[e](f);return this}return c=$.extend({range:.5,anchor:n,init:r,on:r,off:r,delay:0},f),h=$(this),c.init&&c.init(h),h[s](o,-1)[i](function(e){window.clearTimeout(p),p=window.setTimeout(function(){var t=parseInt(h[s](o));if(t==0||t==-1)if(e>=-1*c[u]&&e<=c[u]){h[s](o,1),c.on&&c.on(h);return}if(t==1||t==-1)if(e<-1*c[u]||e>=c[u]){h[s](o,0),c.off&&c.off(h);return}},c.delay)},{anchor:c[a]},e),h},$.fn[f]=function(){var n,r;if(this[t]>1){for(n=0;n<this[t];n++)$(this[n])[f]();return this}return r=$(this),r[c](o,0)[l](e),r},$.fn[i]=function(e,r,o){var u,f,l,c,S;if(this[t]>1){for(u=0;u<this[t];u++)$(this[u])[i](e,r,o);return this}return o||(o=i),f=$.extend({anchor:n,direction:"both",scope:h,easing:0},r),l=$(this),l[s](o+p)||l[s](o+p,E++),c=l[s](o+p),S=d+o+"-"+c,b.off(S).on(S,function(){var t,r=l.offset()[n],i=l.outerHeight(),s=w[v]();switch(f.scope){default:case h:switch(f[a]){default:case n:t=(r-b[m]())/i*-1;break;case g:t=(r-b[m]()-(b[v]()-i)/2)/i*-1;break;case y:t=(r-b[m]()-(b[v]()-i))/i*-1}break;case"window":switch(f[a]){default:case n:t=(r-b[m]())/b[v]()*-1;break;case g:t=(r-b[m]()-(b[v]()-i)/2)/b[v]()*-1;break;case y:t=(r-b[m]()-(b[v]()-i))/b[v]()*-1}}f.direction=="forwards"?t=Math.max(0,t):f.direction=="backwards"&&(t=Math.min(0,t)),t>0?t=Math.max(0,t-f.easing/100):t<0&&(t=Math.min(0,t+f.easing/100)),e(t,l)}).trigger("scroll"),l},$.fn[l]=function(e){var n,r,o,u;if(this[t]>1){for(n=0;n<this[t];n++)$(this[n])[l](e);return this}return e||(e=i),r=$(this),r[s](e+p)?(o=r[s](e+p),u=d+e+"-"+o,b.off(u),r[c](e+p),r):r}})();

					// Apply scrollgress to banner.
						$banner.scrollwatch({
							delay:		0,
							range:		1,
							anchor:		'top',
							on:			function() { $header.addClass('alt reveal'); },
							off:		function() { $header.removeClass('alt'); }
						});

				});

			}

	});

})(jQuery);