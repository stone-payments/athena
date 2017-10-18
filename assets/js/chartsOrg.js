$(function() {
  let myChart = null;
  let languages = null;
  let issuesChart = null;
  let openSourceChart = null;
  let readmeChart = null;
  let LicenseType = null;
  let startDay = moment().startOf('month').format('YYYY-MM-DD');
  let lastDay = moment().format("YYYY-MM-") + moment().daysInMonth();
  colors = ['#0e6251', '#117864', '#148f77', '#17a589', '#1abc9c', '#48c9b0', '#76d7c4', '#a3e4d7', '#d1f2eb',
    '#fef5e7', '#fdebd0', '#fad7a0', '#f8c471', '#f5b041', '#f39c12', '#d68910', '#b9770e', '#9c640c', '#7e5109'
  ]
  colorStone = ['#0B3B1F', '#1DAC4B', '#380713', '#74121D', '#C52233', '#595708', '#657212', '#ABC421']

  $('#name').keypress(function(e) {
    if (e.which == 13) { //Enter key pressed
      $('#find').click(); //Trigger search button click event
    }
  });
  $("#find").click(function() {
      $(".content").show();
    name = $("#name").val();
    console.log(name);
    if ($("#org").val()) {
      startDay = JSON.parse($("#org").val()).start;
      lastDay = JSON.parse($("#org").val()).end;
    }
    $.ajax({
      url: 'http://127.0.0.1:5000/LanguagesOrg?name=' + name,
      type: 'GET',
      success: function(response) {
        console.log(response);
        returnedData = JSON.parse(response);
        let labels = returnedData.map(function(num) {
          return num.name;
        });
        let dataSize = returnedData.map(function(num) {
          return num.size;
        });
        console.log(dataSize);
        if (languages != null) {
          languages.destroy();
        }
        languages = new Chart(document.getElementById("languages"), {
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
                  suggestedMax: 100,
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
        if (languages != null) {
          languages.destroy();
        }
      }
    });
    $.ajax({
      url: 'http://127.0.0.1:5000/CommitsOrg?name=' + name + '&startDate=' + startDay + '&endDate=' + lastDay,
      type: 'GET',
      success: function(response) {
        console.log(response);
        returnedData = JSON.parse(response);
        console.log(response);
        let labelsCommit = returnedData.map(function(num) {
          return num.day;
        });
        let dataCommits = returnedData.map(function(num) {
          return num.number;
        });
        let ctx = document.getElementById("myChart").getContext('2d');
        if (myChart != null) {
          myChart.destroy();
        }
        myChart = new Chart(ctx, {
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
        if (myChart != null) {
          myChart.destroy();
        }
      }
    });
    $.ajax({
      url: 'http://127.0.0.1:5000/RepoMembers?name=' + name,
      type: 'GET',
      success: function(response) {
        console.log(response);
        returnedData = JSON.parse(response);
        $("#members").empty();
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
          $("#members").append(html);
        });
      },
      error: function(error) {
        console.log(error);
        $("#members").empty();
      }
    });
    $.ajax({
      url: 'http://127.0.0.1:5000/OpenSource?name=' + name,
      type: 'GET',
      success: function(response) {
        console.log(response);
        returnedData = JSON.parse(response);
        let openSource = Number(returnedData[0]['openSource']);
        let notOpenSource = Number(returnedData[0]['notOpenSource']);
        console.log(notOpenSource);
        if (openSourceChart != null) {
          openSourceChart.destroy();
        }
        openSourceChart = new Chart(document.getElementById("openSourceChart"), {
          type: 'doughnut',
          data: {
            labels: ['openSource', 'Private'],
            datasets: [{
              label: "Languages (%)",
              backgroundColor: ['#0B3B1F', '#C52233'],
              borderWidth: 1,
              data: [openSource, notOpenSource]
            }]
          },
          options: {
            responsive: true
          }
        });
      },
      error: function(error) {
        console.log(error);
        if (openSourceChart != null) {
          openSourceChart.destroy();
        }
      }
    });
    $.ajax({
      url: 'http://127.0.0.1:5000/readmeOrg?name=' + name,
      type: 'GET',
      success: function(response) {
        console.log(response);
        returnedData = JSON.parse(response);
        let ok = Number(returnedData[0]['ok']);
        let poor = Number(returnedData[0]['poor']);
        let none = Number(returnedData[0]['bad']);
        if (readmeChart != null) {
          readmeChart.destroy();
        }
        readmeChart = new Chart(document.getElementById("readmeChart"), {
          type: 'doughnut',
          data: {
            labels: ['OK', 'Poor', 'None'],
            datasets: [{
              label: "Languages (%)",
              backgroundColor: ['#0B3B1F', '#ABC421', '#C52233'],
              borderWidth: 1,
              data: [ok, poor, none]
            }]
          },
          options: {
            responsive: true
          }
        });
      },
      error: function(error) {
        console.log(error);
        if (readmeChart != null) {
          readmeChart.destroy();
        }
      }
    });
    $.ajax({
      url: 'http://127.0.0.1:5000/LicenseType?name=' + name,
      type: 'GET',
      success: function(response) {
        console.log(response);
        returnedData = JSON.parse(response);
        let labelsLicense = returnedData.map(function(num) {
          return num.day;
        });
        let dataLicense = returnedData.map(function(num) {
          return num.number;
        });
        if (LicenseType != null) {
          LicenseType.destroy();
        }
        LicenseType = new Chart(document.getElementById("LicenseType"), {
          type: 'bar',
          data: {
            labels: labelsLicense,
            datasets: [{
              label: "Languages (%)",
              backgroundColor: ['rgb(168,169,173)', '#0B3B1F', '#1DAC4B', '#380713', '#74121D', '#C52233', '#595708', '#657212', '#ABC421'],
              borderWidth: 1,
              data: dataLicense
            }]
          },
          options: {
            tooltips: {
              mode: 'index',
              intersect: false
            },
            scales: {
              xAxes: [{
                ticks: {
                  autoSkip: false,
                  responsive: true
                }
              }],
              yAxes: [{
                ticks: {
                  autoSkip: true,
                  maxTicksLimit: 100,
                  responsive: true,
                  beginAtZero: true
                }
              }]
            },
          }
        });
      },
      error: function(error) {
        console.log(error);
        if (LicenseType != null) {
          LicenseType.destroy();
        }
      }
    });
    $.ajax({
      url: 'http://127.0.0.1:5000/IssuesOrg?name=' + name + '&startDate=' + startDay + '&endDate=' + lastDay,
      type: 'GET',
      success: function(response) {
        returnedData = JSON.parse(response);
        console.log(returnedData[0]);
        let labelsIssues1 = returnedData[0].map(function(num) {
          return num.day;
        });
        let dataIssues1 = returnedData[0].map(function(num) {
          return num.number;
        });
        let dataIssues2 = returnedData[1].map(function(num) {
          return num.number;
        });
        let ctx = document.getElementById("issuesChart").getContext('2d');
        if (issuesChart != null) {
          issuesChart.destroy();
        }
        issuesChart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: labelsIssues1,
            datasets: [{
                label: 'num of Closed Issues',
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
                label: 'num of Created Issues',
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
  });
});
