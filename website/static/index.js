function deleteCourse(courseId){
    fetch('/delete-course', {
    method: 'POST',
    body: JSON.stringify({courseId: courseId}),
    }).then((_res) => {
        window.location.href = "/home";
    });  
}

function deletePDF(pdfId){
    fetch('/delete-note', {
    method: 'POST',
    body: JSON.stringify({pdfId: pdfId}),
    }).then((_res) => {
        window.location.href = "/home";
    });  
}