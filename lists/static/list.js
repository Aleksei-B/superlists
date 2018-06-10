window.Superlists = {};

window.Superlists.updateItems = function(url) {
  $.get(url).done(function (response) {
	  if (!response.items) {return;}
	  var rows = '';
	  for (var i=0; i<response.items.length; i++) {
		var item = response.items[i];
		rows += '\n<tr><td>' + (i+1) + ': ' + item.text + '</td></tr>';
	  }
	  $('#id_list_table').html(rows);
	});
};

window.Superlists.markAsRead = function(event) {
  event.preventDefault();
  var href = $(event.currentTarget).attr('href');
  $.post(href, {'csrfmiddlewaretoken': $('#id_item_form input[name="csrfmiddlewaretoken"]').val()});
  if ($(event.currentTarget).text() == 'mark as read') {
    $(event.currentTarget).replaceWith('<p class="pull-right">already read</p>');
  } else {
    $('#id_notify_list .pull-right').replaceWith('<p class="pull-right">already read</p>');
  }
};

window.Superlists.initialize = function (params) {
  $('input[name="text"]').on('keypress click', function () {
    $('.has-error').hide();
  });

  $('#id_notify_list .pull-right').on('click', window.Superlists.markAsRead);
  $('#id_notify_list li:last-child a').on('click', window.Superlists.markAsRead);

  if (params) {
    window.Superlists.updateItems(params.listApiUrl);

	var form = $('#id_item_form');
	form.on('submit', function(event) {
	  event.preventDefault();
	  $.post(params.itemsApiUrl, {
		'list': params.listId,
		'text': form.find('input[name="text"]').val(),
		'csrfmiddlewaretoken': form.find('input[name="csrfmiddlewaretoken"]').val(),
      }).done(function () {
		$('.has-error').hide();
		window.Superlists.updateItems(params.listApiUrl);
	  }).fail(function (xhr) {
		$('.has-error').show();
		if (xhr.responseJSON) {
		  $('.has-error .help-block').text(xhr.responseJSON.text || xhr.responseJSON.non_field_errors);
		} else {
		  $('.has-error .help-block').text('Error talking to server. Please try again.');
		}
	  });
    });
  }
};
