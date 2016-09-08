$(function() {

  window.data = [];
  var load;

  window.graphs = [
    {'div': '#graph1', 'col': 'count_pv', 'title': 'Count Pageviews' },
    {'div': '#graph2', 'col': 'count_artwork_pv', 'title': 'Count Artwork Pageviews' },
    {'div': '#graph3', 'col': 'count_artist_pv', 'title': 'Count Artist Pageviews' },
    {'div': '#graph4', 'col': 'count_article_pv', 'title': 'Count Article Pageviews' },
    {'div': '#graph5', 'col': 'inquiries', 'title': 'Inquiries' },
    {'div': '#graph6', 'col': 'three_way_handshakes', 'title': 'Three Way Handshakes' },
    {'div': '#graph7', 'col': 'three_way_handshakes_within_seven_days', 'title': 'Three Way Handshakes Within Seven Days' },
    {'div': '#graph8', 'col': 'purchases', 'title': 'Purchases' },
    {'div': '#graph9', 'col': 'total_purchase_price', 'title': 'Total Purchase Price' },
    {'div': '#graph10', 'col': 'accounts_created', 'title': 'Accounts Created' }
  ];

  function changeHeader() {
    var bodyElement = $(".bl");
    var settingsContainer = $(".test-and-settings-container");
    if (this.scrollY > 506) {
      settingsContainer.css('position', 'fixed');
      settingsContainer.css('top', '50px');
      $('.blocking-div').show();
    } else {
      settingsContainer.css('position', 'static');
      settingsContainer.css('top', 'auto');
      $('.blocking-div').hide();
    }
  }
  
  window.addEventListener("scroll", changeHeader, false);

  $('.recent-ab-tests p').click(function() {
    $.scrollTo(510, 600);
    getTestName.apply(this);
  });

  $('.ab-test-input').focus(function() {
    $(this).next().show();
  }).blur(function() {
    $(this).next().hide();
  });

  $('.search-icon').click(function() {
    $('.ab-test-input').focus();
  });

  $('.ab-dataset p').mousedown(function() {
    var test = $(this).text();
    $('.submit').attr('data-ab-test', toCamelCase(test)); 
    getStartEnd(test);
    if (test.length > 18) { test = test.slice(0, 21) + '...' };
    $('.ab-test-input').val(test);
    $('.ab-test-input').addClass('selected');
  });

  $('.submit').click(function() {
    getData($('.submit').attr('data-ab-test'), 
            $('.start-date-input').val(),
            $('.end-date-input').val());
    $('.start-date-input').addClass('selected');
    $('.end-date-input').addClass('selected');
    loading.apply($('.submit'));
  });

  var getTestName = function() {
    var test = $(this).text();
    console.log(test);
    $('.submit').attr('data-ab-test', toCamelCase(test)); 
    getStartEnd(test);
    if (test.length > 18) { test = test.slice(0, 21) + '...' };
    $('.ab-test-input').val(test);
    $('.ab-test-input').addClass('selected');
  };

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
        getD3Data();
        var exp = $('.submit').attr('data-ab-test').replace(/_/g, ' ');
        $('.ab-test-header h1').text(toTitleCase(exp));
        clearInterval(load);
        $('.submit h3').text('CALCULATE')
      }
    });
  };

  var getD3Data = function() {
    $.ajax({
      type: 'GET',
      url : "/d3_data",
      success: function(result) {
        result = JSON.parse(result['data']);
        setData(result);
        $.getScript('../static/js/linegraph.js');
      }
    });
  };

  function setData(res) {
    data = res;
  };

  var loading = function() {
    var elem = this.children('h3:first');
    elem.text('LOADING');
    load = setInterval(function() {
      elem.text(elem.text() + '.');
      if (elem.text().length > 10) {
        elem.text(elem.text().slice(0, 7));
      }
    }, 1000);
  };

  function toCamelCase(string) {
    return string.replace(/ /g, '_').toLowerCase();
  };

  function toTitleCase(str) {
    return str.replace(/\w\S*/g, function(txt){
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
  };
});
