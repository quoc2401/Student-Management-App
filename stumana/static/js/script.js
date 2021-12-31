function changeRule() {
    event.preventDefault()
    min_age = document.getElementById('min_age').value
    max_age = document.getElementById('max_age').value
    max_size = document.getElementById('max_size').value

    fetch("/api/change-rule", {
        method: 'POST',
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
            a.className = "alert alert-success"
            a.innerText = "Thay đổi thành công"
        }
        else {
           a.style.display = "block"
           a.className = "alert alert-danger"
           a.innerText = "Có dữ liệu vi phạm ràng buộc"
        }

        $(a).fadeOut(5000)
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
        method: 'POST',
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
            a.className = "alert alert-success"
            a.innerText = "Lưu thành công"
            window.location.reload()
        }
        else {
           a.style.display = "block"
           a.className = "alert alert-danger"
           a.innerText = "Lưu thất bại"
        }

        $(a).fadeOut(3000)
    }).catch(function(err) {
        console.info(err)
    });

}


//button get selected info and add_class
function addClass(class_id) {
    event.preventDefault()
    var items=[];
    $("input.select-item:checked:checked").each(function (index,item) {
        items[index] = item.value;
    });

    if (items.length < 1)
        alert('Chưa có học sinh nào được chọn')
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
            }
            else {
                a.style.display = "block"
                a.className = "alert alert-danger"
                a.innerText = "Thêm thất bại"
            }

            $(a).fadeOut(5000)
        }).catch(function(err) {
            console.info(err)
        });

}


$(document).ready(function() {
    var main_route = (window.location.pathname.split("/")[1]);
    $('.nav-item').removeClass('active');
    $('#nav_' + main_route).addClass('active');
    $(document).on('click', '.nav-item', function (e) {
        $('.nav-item').removeClass('active');
        $('#nav_' + main_route).addClass('active');
    });
})