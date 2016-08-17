$(function() {

  function toCamelCase(string) {
    return string.replace(/ /g, '_').toLowerCase();
  };

  $('.ab-test-input').focus(function() {
    $(this).next().show();
  }).blur(function() {
    $(this).next().hide();
  });

  $('.search-icon').click(function() {
    $('.ab-test-input').focus();
  });

  $('.ab-dataset p').live('mousedown', function() {
    var test = $(this).text();
    $('.submit').attr('data-ab-test', toCamelCase(test)); 
    getStartEnd(test);
    if (test.length > 18) { test = test.slice(0, 18) + '...' };
    $('.ab-test-input').val(test);
    $('.ab-test-input').addClass('selected');
  });

  $('.submit').click(function() {
    getData($('.submit').attr('data-ab-test'), 
            $('.start-date-input').val(),
            $('.end-date-input').val());
  });

  var getStartEnd = function(abTest) {
    $.ajax({
      type: 'GET',
      url : "/test_dates",
      data: toCamelCase(abTest),
      success: function(result) {
        $('.start-date-input').val(result['data'][0]);
        $('.end-date-input').val(result['data'][1]);
      }
    })
  };

  var getData = function(abTest, start, end) {
    $.ajax({
      type: 'GET',
      url : "/test_data",
      data: abTest + ',' + start + ',' + end,
      success: function(result) {
        $('.overview-tables').replaceWith(result);
      }
    })
  };
});
