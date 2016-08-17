$(function() {

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
    getData(test);
    if (test.length > 17) { test = test.slice(0, 17) + '...' };
    $('.ab-test-input').val(test);
    $('.ab-test-input').addClass('selected');
  });

  var getData = function(abTest) {
    abTest = abTest.replace(/ /g, '_').toLowerCase();
    $.getJSON('/test_data', {
      abTest: abTest
    }, function(data) {
      console.log(data.overview);
      $(".ab-test-header h1").html(data.overview[0][0][0]);
    });
  };
});
