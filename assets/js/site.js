var ajaxExtra = {};
ajaxExtra.ratingRound = {};

// get elements
function $() {
        var a = new Array();
        var l = arguments.length;
        for (var i=0;i<arguments.length;i++) {
                var e = arguments[i];
                if (typeof e=='string') e = document.getElementById(e);
                if (l==1) return e;
                a.push(e);
        }
        return a;
}

function voteMakeActiveStar(textID,num) {
        try {
                for (var i=1;i<=5;i++) {
                        var el = $('vote_'+textID+'_'+i);
                        el.src = num < i ? '/i/site/star_deactive.png' : '/i/site/star_active.png';
                }
        } catch(e) {}
        return false;
}

function voteMakeDeativeStar(textID,rating) {
        try {
                if (ajaxExtra.ratingRound[textID]) rating = ajaxExtra.ratingRound[textID];
                for (var i=1;i<=5;i++) {
                        var el = $('vote_'+textID+'_'+i);
                        el.src = rating < i ? '/i/site/star_deactive.png' : '/i/site/star_active.png';
                }
        } catch(e) {}
        return false;
}

var lastActionElement = new Array();
var commentActionForm = new Array();

function makeForumReplyForm(element, subj, parent_id) {
	var id = 'forum_form';
	closeReplyForm(id);
	if (typeof(element) == 'string') {
		element = $(element);
	}

	if (!element) return true;

	// get comment form to variable
	if (!commentActionForm[id]) {
		var commentActionFormElement = $(id);
		if (!commentActionFormElement) return true;
		commentActionForm[id] = commentActionFormElement.innerHTML;
		commentActionFormElement.parentNode.removeChild(commentActionFormElement);
	}

	// src элемента
	var newElement = document.createElement('div');
	newElement.innerHTML = commentActionForm[id];

	element.appendChild(newElement);
	lastActionElement[id] = newElement;

	newElement.style.border = '1px solid #000';
	newElement.style.padding = '5px 5px 5px 5px';
	if (subj) {
		var selement = $('comment_body');
		if (selement) {
		    selement.value = subj;
        }
	}
	if (parent_id) {
        var parent_element = $('comment_parent');
        if (parent_element) {
            parent_element.value = parent_id;
        }
    }

	return false;
}

function closeReplyForm(id) {
	var el = lastActionElement[id];
	if (typeof(el) != 'object') return false;

	el.parentNode.removeChild(el);
	lastActionElement[id] = '';
}

function karmed(id) {
    var c = $('ch' + id);
    c.style.display = 'block';
    var a = $('ca' + id);
    a.style.display = 'none';
    return false;
}


function marqueeStart(id){
    var box = document.getElementById(id);
    var block = box.firstElementChild;

    var marquee = document.createElement('marquee');
    marquee.setAttribute('scrollamount', '2');
    box.appendChild(marquee);
    marquee.appendChild(block)
    block.style.display = 'block';
}    

