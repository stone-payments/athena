$(function() {
  let commitsCharts = null;
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
  setInterval(function(){
   $('#find').click();
 }, 300000);
  $("#find").click(function() {
      $(".content").show();
    name = $("#name").val();
    if ($("#org").val()) {
      startDay = JSON.parse($("#org").val()).start;
      lastDay = JSON.parse($("#org").val()).end;
    }
    $.ajax({
      url: address+'/get_org_info?name=' + name,
      type: 'GET',
      success: function(response) {
        returnedData = JSON.parse(response);
        let url = String(returnedData[0]['avatarUrl']);
        let repoCount = String(returnedData[0]['repoCount']);
        let membersCount = String(returnedData[0]['membersCount']);
        let teamsCount = String(returnedData[0]['teamsCount']);
        let projectCount = String(returnedData[0]['projectCount']);
        let orgName = String(returnedData[0]['org']);
        let orgLastUpdated = String(returnedData[0]['db_last_updated']);
        $('#avatar').attr("src", url);
        $('#membersCount').text(membersCount + " Members");
        $('#orgName').text(orgName);
        $('#repoCount').text(repoCount + " Repositories");
        $('#teamsCount').text(teamsCount + " Teams");
        $('#projectCount').text(projectCount + " Projects");
        $('#orgLastUpdated').html('<i class="fa fa-clock-o"></i> '+ orgLastUpdated + ' minutes ago');
//        if (following == '-'){
//          $(".content").hide();
//          $(document).ready(function() {
//        		$.notify({
//        			icon: 'pe-7s-close-circle',
//        			message: "User does not exist"
//        		}, {
//        			type: 'danger',
//        			timer: 4000
//        		});
//        	});
//        }
//        else {
//          $(".content").show();
//        }
      },

      error: function(error) {
        console.log(error);
      }
    });
    $.ajax({
      url: address+'/get_languages_org?name=' + name,
      type: 'GET',
      success: function(response) {
        returnedData = JSON.parse(response);
        let labels = returnedData.map(function(num) {
          return num.languages;
        });
        let dataSize = returnedData.map(function(num) {
          return num.count;
        });
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
      url: address+'/get_commits_org?name=' + name + '&startDate=' + startDay + '&endDate=' + lastDay,
      type: 'GET',
      success: function(response) {
        returnedData = JSON.parse(response);
        let labelsCommit = returnedData.map(function(num) {
          return num.day;
        });
        let dataCommits = returnedData.map(function(num) {
          return num.count;
        });
        let ctx = document.getElementById("commitsCharts").getContext('2d');
        if (commitsCharts != null) {
          commitsCharts.destroy();
        }
        commitsCharts = new Chart(ctx, {
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
        if (commitsCharts != null) {
          commitsCharts.destroy();
        }
      }
    });
    $.ajax({
      url: address+'/get_open_source_org?name=' + name,
      type: 'GET',
      success: function(response) {
        returnedData = JSON.parse(response);
        let labelsCommit = returnedData.map(function(num) {
          return num.openSource;
        });
        let dataCommits = returnedData.map(function(num) {
          return num.count;
        });
        let openSource = Number(returnedData[0]['openSource']);
        let notOpenSource = Number(returnedData[0]['notOpenSource']);
        if (openSourceChart != null) {
          openSourceChart.destroy();
        }
        openSourceChart = new Chart(document.getElementById("openSourceChart"), {
          type: 'doughnut',
          data: {
            labels: labelsCommit,
            datasets: [{
              label: "",
              backgroundColor: ['#C52233', '#0B3B1F'],
              borderWidth: 1,
              data: dataCommits
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
      url: address+'/get_readme_org?name=' + name,
      type: 'GET',
      success: function(response) {
        returnedData = JSON.parse(response);
        let labelsReadme = returnedData.map(function(num) {
          return num.status;
        });
        let dataReadme = returnedData.map(function(num) {
          return num.count;
        });
        if (readmeChart != null) {
          readmeChart.destroy();
        }
        readmeChart = new Chart(document.getElementById("readmeChart"), {
          type: 'doughnut',
          data: {
            labels: labelsReadme,
            datasets: [{
              label: "",
              backgroundColor: [ '#ABC421', '#0B3B1F', '#C52233'],
              borderWidth: 1,
              data: dataReadme
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
      url: address+'/get_license_type_org?name=' + name,
      type: 'GET',
      success: function(response) {
        returnedData = JSON.parse(response);
        let labelsLicense = returnedData.map(function(num) {
          return num.license;
        });
        let dataLicense = returnedData.map(function(num) {
          return num.count;
        });
        if (LicenseType != null) {
          LicenseType.destroy();
        }
        LicenseType = new Chart(document.getElementById("LicenseType"), {
          type: 'bar',
          data: {
            labels: labelsLicense,
            datasets: [{
              label: "License type",
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
      url: address+'/get_issues_org?name=' + name + '&startDate=' + startDay + '&endDate=' + lastDay,
      type: 'GET',
      success: function(response) {
        returnedData = JSON.parse(response);
        let labelsIssues1 = returnedData[0].map(function(num) {
          return num.day;
        });
        let dataIssues1 = returnedData[0].map(function(num) {
          return num.count;
        });
        let dataIssues2 = returnedData[1].map(function(num) {
          return num.count;
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
