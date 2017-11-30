$(function() {
  let commmit_chart = null;
  let stats_chart = null;
  let avatar = null;
  let startDay = moment().startOf('month').format('YYYY-MM-DD');
  let lastDay = moment().format("YYYY-MM-") + moment().daysInMonth();
  colors = ['#0e6251', '#117864', '#148f77', '#17a589', '#1abc9c', '#48c9b0', '#76d7c4', '#a3e4d7', '#d1f2eb',
    '#fef5e7', '#fdebd0', '#fad7a0', '#f8c471', '#f5b041', '#f39c12', '#d68910', '#b9770e', '#9c640c', '#7e5109'
  ]
  colorStone = ['#0B3B1F', '#1DAC4B', '#380713', '#74121D', '#C52233', '#595708', '#657212', '#ABC421']

  let xhr;
  $('#name').autoComplete({
    minChars: 1,
    source: function(term, response) {
      try {
        xhr.abort();
      } catch (e) {}
      xhr = $.getJSON(address+'/get_user_login?name=' + term, function(result) {
        let returnedData = result.map(function(num) {
          return num.data;
        });
        response(returnedData);
      });
    }
  });
  $('#name').keypress(function(e) {
    if (e.which == 13) { //Enter key pressed
      $('#find').click(); //Trigger search button click event
    }
  });
  $("#find").click(function() {
    name = $("#name").val();
    if ($("#userRangeDate").val()) {
      startDay = JSON.parse($("#userRangeDate").val()).start;
      lastDay = JSON.parse($("#userRangeDate").val()).end;
    }
    $.ajax({
      url: address+'/get_avatar?login=' + name,
      type: 'GET',
      success: function(response) {
        returnedData = JSON.parse(response);
        let url = String(returnedData[0]['avatar']);
        let username = String(returnedData[0]['login']);
        let following = String(returnedData[0]['following']);
        let followers = String(returnedData[0]['followers']);
        let pullrequests = String(returnedData[0]['pullrequests']);
        let contributed = String(returnedData[0]['contributed']);
        $('#avatar').attr("src", url);
        $('#username').text(username);
        $('#contributed').text(contributed + " Contributed Repositories");
        $('#pullrequests').text(pullrequests + " Pull Requests");
        $('#followers').text(followers + " Followers");
        $('#following').text(following + " Following");
        if (following == '-'){
          $(".content").hide();
          $(document).ready(function() {
        		$.notify({
        			icon: 'pe-7s-close-circle',
        			message: "User does not exist"
        		}, {
        			type: 'danger',
        			timer: 4000
        		});
        	});
        }
        else {
          $(".content").show();
        }
      },

      error: function(error) {
        console.log(error);
      }
    });
    $.ajax({
      url: address+'/get_user_commit?name=' + name + '&startDate=' + startDay + '&endDate=' + lastDay,
      type: 'GET',
      success: function(response) {
        returnedData = JSON.parse(response);
        let labelsCommit = returnedData.map(function(num) {
          return num.day;
        });
        let dataCommits = returnedData.map(function(num) {
          return num.number;
        });
        let ctx = document.getElementById("commmit_chart").getContext('2d');
        if (commmit_chart != null) {
          commmit_chart.destroy();
        }
        commmit_chart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: labelsCommit,
            datasets: [{
              label: 'num of Commits',
              data: dataCommits,
              backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
              ],
              borderColor: [
                'rgba(255,99,132,1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
              ],
              borderWidth: 1,
              lineTension: 0
            }]
          },
          options: {
            maintainAspectRatio: true,
            tooltips: {
              mode: 'index',
              intersect: false
            },
            scales: {
              xAxes: [{
                ticks: {
                  autoSkip: labelsCommit.length > 31 ? true : false,
                  beginAtZero: true,
                  responsive: true,
                }
              }],
              yAxes: [{
                ticks: {
                  suggestedMax: 10,
                  beginAtZero: true,
                  callback: function(value, index, values) {
                    if (Math.floor(value) === value) {
                      return value;
                    }
                  }
                }
              }]
            }
          },
        });
      },
      error: function(error) {
        console.log(error);
      }
    });
    $.ajax({
      url: address+'/get_user_contributed_repo?name=' + name + '&startDate=' + startDay + '&endDate=' + lastDay,
      type: 'GET',
      success: function(response) {
        returnedData = JSON.parse(response);
        $("#contributed_repo").empty();
        returnedData.map(function(num) {
          memberName = num.member;
          html = `<tr>
                        <td style="width:10px;">
                                <i class="pe-7s-angle-right-circle"></i>
                        </td>
                        <td>${memberName}</td>
                        <td class="td-actions text-right">
                        </td>
                    </tr>`
          $("#contributed_repo").append(html);
        });
      },
      error: function(error) {
        console.log(error);
      }
    });
    $.ajax({
      url: address+'/get_user_team?name=' + name,
      type: 'GET',
      success: function(response) {
        returnedData = JSON.parse(response);
        $("#user_teams").empty();
        returnedData.map(function(num) {
          memberName = num.teams;
          html = `<tr>
                        <td style="width:10px;">
                                <i class="pe-7s-angle-right-circle"></i>
                        </td>
                        <td>${memberName}</td>
                        <td class="td-actions text-right">
                        </td>
                    </tr>`
          $("#user_teams").append(html);
        });
      },
      error: function(error) {
        console.log(error);
      }
    });
    $.ajax({
      url: address+'/get_user_stats?name=' + name + '&startDate=' + startDay + '&endDate=' + lastDay,
      type: 'GET',
      success: function(response) {
        returnedData = JSON.parse(response);
        let labelsIssues1 = returnedData[0].map(function(num) {
          return num.day;
        });
        let dataIssues1 = returnedData[0].map(function(num) {
          return num.number;
        });
        let dataIssues2 = returnedData[1].map(function(num) {
          return num.number;
        });
        let ctx = document.getElementById("stats_chart").getContext('2d');
        if (stats_chart != null) {
          stats_chart.destroy();
        }
        stats_chart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: labelsIssues1,
            datasets: [{
                label: 'num of Additions',
                data: dataIssues1,
                backgroundColor: [
                  'rgba(54, 162, 235, 0.2)',
                  'rgba(255, 206, 86, 0.2)',
                  'rgba(75, 192, 192, 0.2)',
                  'rgba(153, 102, 255, 0.2)',
                  'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                  'rgba(54, 162, 235, 1)',
                  'rgba(255, 206, 86, 1)',
                  'rgba(75, 192, 192, 1)',
                  'rgba(153, 102, 255, 1)',
                  'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1,
                lineTension: 0
              },
              {
                label: 'num of Deletions',
                data: dataIssues2,
                backgroundColor: [
                  'rgba(255, 99, 132, 0.2)',
                  'rgba(54, 162, 235, 0.2)',
                  'rgba(255, 206, 86, 0.2)',
                  'rgba(75, 192, 192, 0.2)',
                  'rgba(153, 102, 255, 0.2)',
                  'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                  'rgba(255,99,132,1)',
                  'rgba(54, 162, 235, 1)',
                  'rgba(255, 206, 86, 1)',
                  'rgba(75, 192, 192, 1)',
                  'rgba(153, 102, 255, 1)',
                  'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1,
                lineTension: 0
              }
            ]
          },
          options: {
            tooltips: {
              mode: 'index',
              intersect: false
            },
            scales: {
              xAxes: [{
                ticks: {
                  autoSkip: labelsIssues1.length > 31 ? true : false,
                  responsive: true
                }
              }],
              yAxes: [{
                ticks: {
                  suggestedMax: 10,
                  beginAtZero: true,
                  callback: function(value, index, values) {
                    if (Math.floor(value) === value) {
                      return value;
                    }
                  }
                }
              }]
            },
          }
        });
      },
      error: function(error) {
        console.log(error);
      }
    });
      $(".content").show();
  });
});
