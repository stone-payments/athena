$(function() {
  let commitsCharts = null;
  let pieChart = null;
  let issuesChart = null;
  let startDay = moment().startOf('month').format('YYYY-MM-DD');
  let lastDay = moment().format("YYYY-MM-") + moment().daysInMonth();
  var orgSelector = "stone-payments";
   $('#orgSelector').on('change', function() {
     orgSelector = $('#orgSelector').val();
  }),
  colors = ['#0e6251', '#117864', '#148f77', '#17a589', '#1abc9c', '#48c9b0', '#76d7c4', '#a3e4d7', '#d1f2eb',
    '#fef5e7', '#fdebd0', '#fad7a0', '#f8c471', '#f5b041', '#f39c12', '#d68910', '#b9770e', '#9c640c', '#7e5109'
  ]

  let xhr;
  $('#name').autoComplete({
    minChars: 1,
    source: function(term, response) {
      try {
        xhr.abort();
      } catch (e) {}
      xhr = $.getJSON(address+'/get_repo_name?name=' + term+'&org='+ orgSelector, function(result) {
        console.log(orgSelector);
        let returnedData = result.map(function(num) {
          return num.repoName;
        });
        console.log(returnedData);
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
    if ($("#repoRangeDate").val()) {
      startDay = JSON.parse($("#repoRangeDate").val()).start;
      lastDay = JSON.parse($("#repoRangeDate").val()).end;
    }
    $.ajax({
      url: address+'/get_languages_repo?name=' + name+'&org='+ orgSelector,
      type: 'GET',
      success: function(response) {
        returnedData = JSON.parse(response);
        console.log(returnedData);
        let labels = returnedData.map(function(num) {
          return num.language;
        });
        console.log(labels);
        let dataSize = returnedData.map(function(num) {
          return num.size;
        });
        if (pieChart != null) {
          pieChart.destroy();
        }
        pieChart = new Chart(document.getElementById("pie-chart"), {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: "Languages (%)",
              backgroundColor: colors,
              borderWidth: 1,
              data: dataSize
            }]
          },
          options: {
            tooltips: {
              mode: 'index',
              intersect: false
            },
            scales: {
              yAxes: [{
                ticks: {
                  beginAtZero: true,
                  autoSkip: false,
                  maxTicksLimit: 100,
                  responsive: true
                }
              }],
              xAxes: [{
                ticks: {
                  autoSkip: false,
                  responsive: true
                }
              }]
            }
          }
        });
      },
      error: function(error) {
        console.log(error);
      }
    });
//    $.ajax({
//      url: address+'/get_commits_repo?name=' + name + '&startDate=' + startDay + '&endDate=' + lastDay+'&org='+ orgSelector,
//      type: 'GET',
//      success: function(response) {
//        returnedData = JSON.parse(response);
//        let labelsCommit = returnedData.map(function(num) {
//          return num.day;
//        });
//        let dataCommits = returnedData.map(function(num) {
//          return num.number;
//        });
//        let ctx = document.getElementById("commitsCharts").getContext('2d');
//
//        if (commitsCharts != null) {
//          commitsCharts.destroy();
//        }
//        commitsCharts = new Chart(ctx, {
//          type: 'line',
//          data: {
//            labels: labelsCommit,
//            datasets: [{
//              label: 'num of Commits',
//              data: dataCommits,
//              backgroundColor: [
//                'rgba(255, 99, 132, 0.2)',
//                'rgba(54, 162, 235, 0.2)',
//                'rgba(255, 206, 86, 0.2)',
//                'rgba(75, 192, 192, 0.2)',
//                'rgba(153, 102, 255, 0.2)',
//                'rgba(255, 159, 64, 0.2)'
//              ],
//              borderColor: [
//                'rgba(255,99,132,1)',
//                'rgba(54, 162, 235, 1)',
//                'rgba(255, 206, 86, 1)',
//                'rgba(75, 192, 192, 1)',
//                'rgba(153, 102, 255, 1)',
//                'rgba(255, 159, 64, 1)'
//              ],
//              borderWidth: 1,
//              lineTension: 0
//            }]
//          },
//          options: {
//            tooltips: {
//              mode: 'index',
//              intersect: false
//            },
//            scales: {
//              xAxes: [{
//                ticks: {
//                  autoSkip: labelsCommit.length > 31 ? true : false,
//                  beginAtZero: true,
//                  responsive: true
//                }
//              }],
//              yAxes: [{
//                ticks: {
//                  suggestedMax: 10,
//                  beginAtZero: true,
//                  callback: function(value, index, values) {
//                    if (Math.floor(value) === value) {
//                      return value;
//                    }
//                  }
//                }
//              }]
//            }
//          },
//        });
//      },
//      error: function(error) {
//        console.log(error);
//      }
//    });
    $.ajax({
      url: address+'/get_members_repo?name=' + name+'&org='+ orgSelector,
      type: 'GET',
      success: function(response) {
        returnedData = JSON.parse(response);
        $("#members").empty();
        returnedData.map(function(num) {
          memberName = num;
          html = `<tr>
                        <td style="width:10px;">
                                <i class="pe-7s-angle-right-circle"></i>
                        </td>
                        <td>${memberName}</td>
                        <td class="td-actions text-right">
                        </td>
                    </tr>`
          $("#members").append(html);
        });
      },
      error: function(error) {
        console.log(error);
      }
    });
//    $.ajax({
//      url: address+'/get_best_practices_repo?name=' + name+'&org='+ orgSelector,
//      type: 'GET',
//      success: function(response) {
//        returnedData = JSON.parse(response);
//        $("#readme").empty();
//        $("#openSource").empty();
//        $("#license").empty();
//        $("#active").empty();
//        let openSource = String(returnedData[0]['open'][0]['openSource']);
//        let license = (returnedData[0]['open'][0]['licenseType'] == null ? "None" : String(returnedData[0]['open'][0]['license']));
//        let readme = (returnedData[0]['open'][0]['readme'] == null ? "None" : String(returnedData[0]['open'][0]['readme']));
//        let active = Number(returnedData[0]['active']);
//        $("#readme").append(readme);
//        $("#openSource").append(openSource);
//        $("#license").append(license);
//        if (active > 0) {
//          $("#active").append("True").css("text-align", "center");
//        } else {
//          $("#active").append("False").css("text-align", "center");
//        }
//        if (active == 404) {
//          $(".content").hide();
//          $(document).ready(function() {
//            $.notify({
//              icon: 'pe-7s-close-circle',
//              message: "User does not exist"
//            }, {
//              type: 'danger',
//              timer: 1000
//            });
//          });
//        } else {
//          $(".content").show();
//        }
//      },
//      error: function(error) {
//        console.log(error);
//      }
//    });
//    $.ajax({
//      url: address+'/get_issues_repo?name=' + name + '&startDate=' + startDay + '&endDate=' + lastDay,
//      type: 'GET',
//      success: function(response) {
//        returnedData = JSON.parse(response);
//        let labelsIssues1 = returnedData[0].map(function(num) {
//          return num.day;
//        });
//        console.log(labelsIssues1);
//        let dataIssues1 = returnedData[0].map(function(num) {
//          return num.number;
//        });
//        let dataIssues2 = returnedData[1].map(function(num) {
//          return num.number;
//        });
//        let ctx = document.getElementById("issuesChart").getContext('2d');
//        if (issuesChart != null) {
//          issuesChart.destroy();
//        }
//        issuesChart = new Chart(ctx, {
//          type: 'line',
//          data: {
//            labels: labelsIssues1,
//            datasets: [{
//                label: 'num of Closed Issues',
//                data: dataIssues1,
//                backgroundColor: [
//                  'rgba(54, 162, 235, 0.2)',
//                  'rgba(255, 206, 86, 0.2)',
//                  'rgba(75, 192, 192, 0.2)',
//                  'rgba(153, 102, 255, 0.2)',
//                  'rgba(255, 159, 64, 0.2)'
//                ],
//                borderColor: [
//                  'rgba(54, 162, 235, 1)',
//                  'rgba(255, 206, 86, 1)',
//                  'rgba(75, 192, 192, 1)',
//                  'rgba(153, 102, 255, 1)',
//                  'rgba(255, 159, 64, 1)'
//                ],
//                borderWidth: 1
//              },
//              {
//                label: 'num of Created Issues',
//                data: dataIssues2,
//                backgroundColor: [
//                  'rgba(255, 99, 132, 0.2)',
//                  'rgba(54, 162, 235, 0.2)',
//                  'rgba(255, 206, 86, 0.2)',
//                  'rgba(75, 192, 192, 0.2)',
//                  'rgba(153, 102, 255, 0.2)',
//                  'rgba(255, 159, 64, 0.2)'
//                ],
//                borderColor: [
//                  'rgba(255,99,132,1)',
//                  'rgba(54, 162, 235, 1)',
//                  'rgba(255, 206, 86, 1)',
//                  'rgba(75, 192, 192, 1)',
//                  'rgba(153, 102, 255, 1)',
//                  'rgba(255, 159, 64, 1)'
//                ],
//                borderWidth: 1,
//                lineTension: 0
//              }
//            ]
//          },
//          options: {
//            tooltips: {
//              mode: 'index',
//              intersect: false
//            },
//            scales: {
//              xAxes: [{
//                ticks: {
//                  autoSkip: labelsIssues1.length > 31 ? true : false,
//                  beginAtZero: true,
//                  responsive: true
//                }
//              }],
//              yAxes: [{
//                ticks: {
//                  beginAtZero: true,
//                  autoSkip: false,
//                  responsive: true,
//                  stepSize: 1
//                }
//              }]
//            }
//          },
//        });
//      },
//      error: function(error) {
//        console.log(error);
//      }
//    });
    $(".content").show();
  });
});
