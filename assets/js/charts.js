$(function() {
  let myChart = null;
  let pieChart = null;

  $('#name').keypress(function(e){
       if(e.which == 13){//Enter key pressed
           $('#find').click();//Trigger search button click event
       }
   });
    $("#find").click(function() {

        name = $("#name").val();
                    console.log(name);
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
                      backgroundColor: ["#3366CC","#DC3912","#FF9900","#109618","#990099","#3B3EAC","#0099C6","#DD4477","#66AA00","#B82E2E",
                        "#316395","#994499","#22AA99","#AAAA11","#6633CC","#E67300","#8B0707","#329262","#5574A6","#3B3EAC"],
                      borderWidth: 1,
                      data: dataSize
                    }]
                  },
                  options: {
                      scales: {
                          xAxes: [{
                              ticks: {
                                  beginAtZero:true,
                                  autoSkip: false
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
            url: 'http://127.0.0.1:5000/Commits?name='+name,
            type: 'GET',
            success: function(response) {

                returnedData = JSON.parse(response);
                let labelsCommit = returnedData.map(function(num) {
                  return num.month;
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
                  scales: {
                      xAxes: [{
                          ticks: {
                              autoSkip: false
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
    });

});
