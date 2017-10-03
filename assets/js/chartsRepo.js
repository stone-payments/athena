$(function() {
  let myChart = null;
  let pieChart = null;
  let issuesChart = null;
  let teste = null;
  let startDay = moment().startOf('month').format('YYYY-MM-DD');
  let lastDay = moment().format("YYYY-MM-") + moment().daysInMonth();

  colors = ['#0e6251','#117864','#148f77','#17a589','#1abc9c','#48c9b0','#76d7c4','#a3e4d7','#d1f2eb',
  '#fef5e7','#fdebd0','#fad7a0','#f8c471','#f5b041','#f39c12','#d68910','#b9770e','#9c640c','#7e5109']

  $('#name').keypress(function(e){
       if(e.which == 13){//Enter key pressed
           $('#find').click();//Trigger search button click event
       }

   });
    $("#find").click(function() {

        name = $("#name").val();
                    console.log(name);
        if ($("#e1").val()){
          startDay = JSON.parse($("#e1").val()).start;
          lastDay = JSON.parse($("#e1").val()).end;
        }
        $.ajax({
            url: 'http://127.0.0.1:5000/Languages?name='+name,
            type: 'GET',
            success: function(response) {
                console.log(response);
                returnedData = JSON.parse(response);
                let labels = returnedData.map(function(num) {
                  return num.Languages;
              });
              let dataSize = returnedData.map(function(num) {
                return num.Size;
            });
            console.log(dataSize);
            if(pieChart != null){
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
                                  beginAtZero:true,
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
        $.ajax({
            url: 'http://127.0.0.1:5000/Commits2?name='+name+'&startDate='+startDay+'&endDate='+lastDay,
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
            var ctx = document.getElementById("myChart").getContext('2d');

            if(myChart != null){
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
                        borderWidth: 1
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
                            autoSkip: labelsCommit.length > 31 ? true : false,
                              beginAtZero:true,
                              responsive: true

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
            url: 'http://127.0.0.1:5000/RepoMembers?name='+name,
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

            }
        });
        $.ajax({
            url: 'http://127.0.0.1:5000/BestPractices?name='+name,
            type: 'GET',
            success: function(response) {
                console.log(response);
                returnedData = JSON.parse(response);
                $("#readme").empty();
                $("#openSource").empty();
                $("#license").empty();
                $("#active").empty();
                console.log(String(returnedData[0]['open'][0]['licenseType']));
                  let openSource = String(returnedData[0]['open'][0]['openSource']);
                  let license = (returnedData[0]['open'][0]['licenseType'] == null ? "None" : String(returnedData[0]['open'][0]['license']));
                  let readme = String(returnedData[0]['open'][0]['readme']);
                  let active = Number(returnedData[0]['active']);
                  console.log(active);
                $("#readme").append(readme);
                  $("#openSource").append(openSource);
                    $("#license").append(license);
                    if (active > 0){
                      $("#active").append("True").css("text-align", "center");
                    }
                    else{
                      $("#active").append("False").css("text-align", "center");
                    }

                    if (readme == "OK"){
                      $("#readme").css("background-color", "green");
                    }
                    else if (readme == "Poor") {
                        $("#readme").css("background-color", "yellow");
                    }
                    else{
                      $("#readme").css("background-color", "red");
                    }

            },
            error: function(error) {
              console.log(error);

            }
        });

        $.ajax({
            url: 'http://127.0.0.1:5000/Issues?name='+name+'&startDate='+startDay+'&endDate='+lastDay,
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


            var ctx = document.getElementById("issuesChart").getContext('2d');

            if(issuesChart != null){
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
                        borderWidth: 1
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
                        borderWidth: 1
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
                            autoSkip: labelsIssues1.length > 31 ? true : false,
                              beginAtZero:true,
                              responsive: true

                          }
                      }],
                      yAxes: [{
                          ticks: {
                              beginAtZero:true,
                              autoSkip: false,
                              responsive: true,
                              stepSize: 1
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
    });

});
