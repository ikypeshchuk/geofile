function testDownloadSpeed() {
    const url = $("#check-url-network-speed-id").val();
    const downloadSize = 500 * 1024;
    var startTime, endTime;

    startTime = (new Date()).getTime();
    fetch(url).then(response => response.blob()).then(() => {
        endTime = (new Date()).getTime();
        setResult();
    });

    function setResult() {
        const duration = (endTime - startTime) / 1000;
        const bitsLoaded = downloadSize * 8;
        const speedBps = Math.round(bitsLoaded / duration);
        const speedKbps = (speedBps / 1024).toFixed(2);
        const speedMbps = (speedKbps / 1024).toFixed(2);
        $("#network-speed-id").val(speedBps)
        console.log("Your connection speed is: " + speedBps + "=Bps, " + speedKbps + "=Kbps, " + speedMbps + "=Mbps" );
    }
}


function calculateTimeDownload(fileSizeBytes, speedBps) {
  return (fileSizeBytes / speedBps).toFixed(3)
}


function sendInputValue(elementId, serverUrl, fieldName) {
  $(elementId).on("change", function postinput(){
    var postData = {[fieldName]: $(this).val()};
    $.ajax({
      url: serverUrl,
      data: JSON.stringify(postData),
      type: "POST",
      contentType: "application/json",
      xhrFields: {withCredentials: true},
    }).done(function(responseData) {
      $(elementId).val("");
      toastr.success("Файл відправлено на опрацювання, очікуйте резутьтату.")
    }).fail(function() {
      $(elementId).val("");
      toastr.error("Йой, щось пішло не так! Спробуйте трохи згодом.")
    });
  });
}


function downloadFile(this_) {
  const downloadUrl = $(this_).data("download-url");
  const filename = $(this_).data("filename");
  const origin_filename = $(this_).data("origin-filename");
  $(this_).addClass('link-disabled')

  fetch(downloadUrl).then(function(response) {
    return response.blob();
  }).then(function(blob) {
    // Create an object URL for the blob
    var url = window.URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.style.display = "none";
    a.href = url;

    // the filename you want
    if (origin_filename) {
      a.download = origin_filename;
    } else {
      a.download = filename;
    }
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);

    // Get current UTC time when download is complete
    var now = new Date();
    try {
        document.getElementById(`${filename}-download-time`).textContent = `, ${now.toISOString()}`;
    } catch {
        $(`#${filename}-download-time`).text(`, ${now.toISOString()}`);
        alert(`Complete download, ${now.toISOString()}`)
    }
    $(this_).removeClass('link-disabled')
  }).catch(function(error) {
    toastr.error("Йой, щось пішло не так! Спробуйте трохи згодом.")
    $(this_).removeClass('link-disabled')
  });
}


function getCookie(name) {
    let cookieArr = document.cookie.split(";");
    for(let i = 0; i < cookieArr.length; i++) {
        let cookiePair = cookieArr[i].split("=");
        if(name === cookiePair[0].trim()) {return decodeURIComponent(cookiePair[1])}
    }
    return null;
}

function createDownloadTimeBox(prefixId) {return `<span id="${prefixId}-download-time"></span>`}


function addNewFileToList(fileData, fileListId) {
  const locationInfo = `${fileData.location.country}, ${fileData.location.region}, ${fileData.location.city}, ${fileData.location.ip}`;

  var fileInfo = `${fileData.download_duration}sec, ${fileData.created_at}<br>${fileData.download_url}`;
  var timeDownload = "replica ";
  var deleteBtn = "";
  var downloadUrl = "";

  if (!fileData.replica) {
    timeDownload = `${calculateTimeDownload(fileData.size, $("#network-speed-id").val())}sec, `;
    deleteBtn = `<br><button data-delete-url="/delete/${fileData.filename}" data-filename="${fileData.filename}" class="btn btn-danger btn-sm" style="margin:5px 0" onclick="deleteFile(this); return false">Delete</button>`;
    downloadUrl = `<br>${timeDownload}<a href="${fileData.download_url}" data-download-url="${fileData.download_url}" data-filename="${fileData.filename}" data-origin-filename="${fileData.origin_filename}" id="${fileData.filename}-link" onclick="downloadFile(this);return false;">Download</a>${createDownloadTimeBox(fileData.filename)}${deleteBtn}`;
  } else {
      fileInfo = `${timeDownload} ${fileInfo}`
  }
  const newDiv = `<div class="text-small top-border" id="${fileData.filename}">${locationInfo}<br>${fileInfo}${downloadUrl}</div>`;

  $(fileListId).prepend(newDiv);
  toastr.success(`Файл: ${fileData.origin_filename}, успішно завантажено на сервер.`)
}


function handleMessageSuccess(data) {
    toastr.success(data.msg)
    try {
        if (data.data.filename) {document.getElementById(`${data.data.filename}`).remove()}
    } catch {}
}


function socketHandlers(serverUrl) {
  let socket = io.connect(serverUrl);

  document.addEventListener("visibilitychange", function() {
    if (!document.hidden && socket.disconnected) {
      socket = io.connect(serverUrl);
    }
  });

  socket.on("connect", function() {
    socket.send("User has connected!");
  });

  socket.on("disconnect", function() {
    socket.send("User has disconnect!");
  });

  socket.on("setUserSID", function(userSID) {
    var existingSID = getCookie("userSID");
    if (!existingSID) {
      document.cookie = `userSID=${userSID}`;
    }
  });

  socket.on("fileUploadSuccessful", function(data) {
    testDownloadSpeed();
    addNewFileToList(data, "#new-list-files-id");
  });

  socket.on("messageSuccess", function(data) {
    handleMessageSuccess(data);
  });

  socket.on("errors", function(msg) {
    toastr.error(msg);
  });
}



function addFileToList(fileData, fileListId) {
  const deleteBtn = `<br><button data-delete-url="/delete/${fileData.filename}" data-filename="${fileData.filename}" style="margin-top:10px" class="btn btn-danger btn-sm" onclick="deleteFile(this); return false">Delete</button>`;
  const locationInfo = `${fileData.location.country}, ${fileData.location.region}, ${fileData.location.city}, ${fileData.location.ip}`

  const link = `<a href="#" data-download-url="${fileData.download_url}" data-filename="${fileData.filename}" id="${fileData.filename}-link" onclick="downloadFile(this);return false;">Download</a>${createDownloadTimeBox(fileData.filename)}`;
  const sizeMb = (fileData.size  / (1024 * 1024)).toFixed(3)
  const download = `${locationInfo}<br>${sizeMb}size mb, ${calculateTimeDownload(fileData.size, $("#network-speed-id").val())}sec, ${link}${deleteBtn}`;
  const newDiv = `<div class="text-small top-border" id="${fileData.filename}" style="padding-top:10px">${download}</div>`;

  $(fileListId).prepend(newDiv);
}


function getListFiles(this_) {
  $(this_).attr("disabled", "disabled");

  $.ajax({
    url: $(this_).data("list-url"),
    type: "GET",
    contentType: "application/json",
  }).done(function(responseData) {
    $("#old-list-files-id").html("")
    responseData.forEach(function(fileData) {
      addFileToList(fileData, "#old-list-files-id", false)
    });
  }).fail(function() {
    toastr.error("Йой, щось пішло не так! Спробуйте трохи згодом.")
    $(this_).removeAttr("disabled")
  })
}

function deleteFile(this_) {
  $(this_).attr("disabled", "disabled");
  $.ajax({
    url: $(this_).data("delete-url"),
    type: "DELETE",
    xhrFields: {withCredentials: true},
  }).done(function(responseData) {
      document.getElementById($(this_).data("filename")).remove()
      toastr.success(`Файл успішно видалено.`)
  }).fail(function() {
    toastr.error("Йой, щось пішло не так! Спробуйте трохи згодом.")
    $(this_).removeAttr("disabled")
  })
}