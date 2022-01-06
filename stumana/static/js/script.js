$(document).ready(function() {
    a = document.getElementById('alert')

    $(a).mouseenter(function() {
        $(this).stop().animate({opacity:'100'})
        $(this).toggleClass('shadow-box')
    })
    $(a).mouseleave(function() {
        $(this).fadeOut(3000)
        $(this).toggleClass('shadow-box')
    })
})

function changeRule() {
    event.preventDefault()
    min_age = document.getElementById('min_age').value
    max_age = document.getElementById('max_age').value
    max_size = document.getElementById('max_size').value

    fetch("/api/change-rule", {
        method: 'PUT',
        body: JSON.stringify({
            'min_age': min_age,
            'max_age': max_age,
            'max_size': max_size
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        console.info(res)
        return res.json()
    }).then(function(data) {
        a = document.getElementById('alert')

        if(data.status == 200) {
            a.style.display = "block"
            a.className = "overlay-alert overlay-alert-success"
            a.innerText = "Thay đổi thành công"
        }
        else {
           a.style.display = "block"
           a.className = "overlay-alert overlay-alert-danger"
           a.innerText = "Có dữ liệu vi phạm ràng buộc"
           console.info(data.err_msg1)
           console.info(data.err_msg2)
        }

        $(a).fadeOut(3000)
    }).catch(function(err) {
        console.info(err)
    })
}

function loadChart(ctx, labels, data, type, colors, borderColors, title) {
        const myChart = new Chart(ctx, {
            type: type,
            data: {
                labels: labels,
                datasets: [{
                    label: title,
                    data: data,
                    backgroundColor: colors,
                    borderColor: borderColors,
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        })
}

function updateMarks(subject_id, student_id, year) {
    event.preventDefault()
    mark15_1_obj = document.getElementsByClassName('mark15_1')
    mark45_1_obj = document.getElementsByClassName('mark45_1')
    mark15_2_obj = document.getElementsByClassName('mark15_2')
    mark45_2_obj = document.getElementsByClassName('mark45_2')
    final_mark1 = document.getElementById('final_mark1').value
    final_mark2 = document.getElementById('final_mark2').value
    mark15_1 = []
    mark45_1 = []
    mark15_2 = []
    mark45_2 = []

    for(let i = 0; i < 5; i++) {
        mark15_1[i] = mark15_1_obj[i].value
        mark15_2[i] = mark15_2_obj[i].value
    }

    for(let i = 0; i < 3; i++) {
        mark45_1[i] = mark45_1_obj[i].value
        mark45_2[i] = mark45_2_obj[i].value
    }

    fetch("/api/update-mark", {
        method: 'PUT',
        body: JSON.stringify({
            'subject_id':subject_id,
            'student_id':student_id,
            'year': year,
            'mark15_1': mark15_1,
            'mark45_1': mark45_1,
            'mark15_2': mark15_2,
            'mark45_2': mark45_2,
            'final_mark1': final_mark1,
            'final_mark2': final_mark2
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        console.info(res)
        return res.json()
    }).then(function(data) {
        a = document.getElementById('alert')

        if(data.status == 200) {
            a.style.display = "block"
            a.className = "overlay-alert overlay-alert-success"
            a.innerText = "Lưu thành công"
        }
        else {
           a.style.display = "block"
           a.className = "overlay-alert overlay-alert-danger"
           a.innerText = "Lưu thất bại!"
           console.info(data.err_msg)
        }

        $(a).fadeOut(3000)
    }).catch(function(err) {
        console.info(err)
    });

}

// input type check all
$(function(){
    l = $("input.select-item").length
    $('.statusbar').text(l+' items, items selected: 0');

        //button select all or cancel
        $("#select-all").click(function () {
            var all = $("input.select-all")[0];
            all.checked = !all.checked
            var checked = all.checked;
            $("input.select-item").each(function (index,item) {
                item.checked = checked;
            });
        });

         //column checkbox select all or cancel
        $("input.select-all").click(function () {
            var checked = this.checked;
            $("input.select-item").each(function (index,item) {
                item.checked = checked;
            });
        });

        //count selected items
        $(".select-all, .select-item, #select-all").click(function () {
            var items=[];
            var count = 0
            var len = $("input.select-item").length
            $("input.select-item:checked:checked").each(function (index,item) {
                items[index] = item.value;
            });
            if (items.length < 1) {
                $('.statusbar').text(len+' items, items selected: '+ count);
            }else {
                for(var i = 0; i < items.length; i++){
                    if (items[i])
                        count++;
                }
                $('.statusbar').text(len+' items, items selected: '+ count);
            }
        });

        //check selected items
        $("input.select-item").click(function () {
            var checked = this.checked;
            checkSelected();
        });

        //check is all selected
        function checkSelected() {
            var all = $("input.select-all")[0];
            var total = $("input.select-item").length;
            var len = $("input.select-item:checked:checked").length;
            all.checked = len===total;
        }
});

//button get selected info and add_class
function addClass(class_id) {
    event.preventDefault()
    var items=[];
    $("input.select-item:checked:checked").each(function (index,item) {
        items[index] = item.value;
    });

    if (items.length < 1)
        alert('Chưa có học sinh nào được chọn!')
    else
        fetch("/api/update-class", {
            method: 'POST',
            body: JSON.stringify({
                'student_id': items,
                'class_id': class_id
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(function(res) {
            console.info(res)
            return res.json()
        }).then(function(data) {
            a = document.getElementById('alert')

            if(data.status == 200) {

                window.location.reload()
                if ($("div #class_id").text().split(":")[1] != undefined)
                    alert("Thêm thành công")
                else
                    alert("Xóa thành công")
            }
            else {
                a.style.display = "block"
                a.className = "overlay-alert overlay-alert-danger"
                a.innerText = "Thêm thất bại"
            }

            $(a).fadeOut(5000)
        }).catch(function(err) {
            console.info(err)
        });
}

function loadMarks(course_id) {
     fetch("/api/load-marks", {
        method: 'POST',
        body: JSON.stringify({
            'course_id': course_id,
            'semester': document.getElementById('semester').value
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        console.info(res)
        return res.json()
    }).then(function(data) {

        if(data.status == 200) {
            marks = data.marks
            console.info(marks)

            for(let i = 0; i < marks.length; i++) {
                marks15 = document.getElementsByClassName('mark15_' + marks[i].student_id)
                marks45 = document.getElementsByClassName('mark45_' + marks[i].student_id)

                for(let j = 0; j < 5; j++) {
                    marks15[j].innerText = marks[i].mark15[j]
                }
                for(let j = 0; j < 3; j++) {
                    marks45[j].innerText = marks[i].mark45[j]
                }
                document.getElementById('final_mark_' + marks[i].student_id).innerText = marks[i].final_mark
                document.getElementById('avg_mark_' + marks[i].student_id).innerText = marks[i].avg_mark
            }
        }
        else {
           console.info("that bai")
        }

    }).catch(function(err) {
        console.info(err)
    })
}

// confirm password
$(document).ready(function() {
  var passOne = $("#n-password").val();
  var passTwo = $("#c-password").val();

  var checkAndChange = function()
  {
    if(passOne.length < 1)
      if($(".confirm").hasClass("alert-success")){
        $(".confirm").removeClass("alert-success").addClass("alert-danger");
        $(".confirm").html("Mật khẩu không giống nhau!");
      }else{
        $(".confirm").html("Mật khẩu không giống nhau!");
      }
    else if($(".confirm").hasClass("alert-danger"))
    {
      if(passOne == passTwo) {
        $(".confirm").removeClass("alert-danger").addClass("alert-success");
        $(".confirm").html("Tiếp tục");
      }
    }
    else
    {
      if(passOne != passTwo){
        $(".confirm").removeClass("alert-success").addClass("alert-danger");
        $(".confirm").html("Mật khẩu không giống nhau!");
      }
    }
  }

  $("input[type=password]").keyup(function(){
    var newPassOne = $("#n-password").val();
    var newPassTwo = $("#c-password").val();

    passOne = newPassOne;
    passTwo = newPassTwo;

    checkAndChange();
  });
});


function classSearch() {
    var keyword = $("#keyword").val()
    if (keyword != undefined && keyword != null) {
        window.location = '/students-marks?keyword=' + keyword;
    }
}

/******************** Filter  ***********************/

function changeContext() {
    document.getElementById("keyword").name = document.getElementById("context").value
}

String.prototype.replaceAt = function(index, replacement) {
    return this.substr(0, index) + replacement + this.substr(index + replacement.length);
}

String.prototype.replaceBetween = function(start, end, what) {
  return this.substring(0, start) + what + this.substring(end);
};

function studentFilter() {
    var context = $("#context").val()
    var keyword = $("#keyword").val()
    var location = window.location
    if (keyword != undefined && keyword != null) {
        if (location.search)
            if (location.search.indexOf(context) === -1)
                location.search = location.search + "&" + context + "=" + keyword
            else {
                var start = location.search.indexOf(context)
                var end =  location.search.indexOf("&", start)
                if (end != -1)
                    location.search = location.search.replaceBetween(start, end, context + "=" + keyword)
                else
                    location.search = location.search.replaceBetween(start, location.search.length,context + "=" + keyword)
            }
        else {
            if (location.search.indexOf(context) === -1)
                location.search = location.search + context + "=" + keyword
            else {
                var start = location.search.indexOf(context)
                var end =  location.search.indexOf("&", start)
                if (end != -1)
                    location.search = location.search.replaceBetween(start, end, context + "=" + keyword)
                else
                    location.search = location.search.replaceBetween(start, location.search.length,context + "=" + keyword)
            }
        }
    }
}

function removeFilter() {
    event.preventDefault()
    var search = window.location.search
    if (search.indexOf('class=') != -1) {
        var start = search.indexOf('class=')
        var end =  search.indexOf("&", start)
        var keep = search.substring(start, end)
    window.location.search = keep
    }
    else
        window.location.search = ''
}

function display0Class() {
    $("#context option[value='class_name']").prop('selected', true)
    $("#keyword").val(0)
    $("#search").click()
}

/**************** Back to top *******************/
$(document).ready(function(){

    //Check to see if the window is top if not then display button
    $(window).scroll(function(){
        if ($(this).scrollTop() > 100) {
            $('.scrollToTop').fadeIn(0);
        } else {
            $('.scrollToTop').fadeOut();
        }
    });

    //Click event to scroll to top
    $('.scrollToTop').click(function(){
        $('html, body').animate({scrollTop : 0},800);
        return false;
    });

});
