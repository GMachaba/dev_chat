$(document).on("click",".add-tag-link",function(e){
    e.preventDefault();
    $link = $(this);
    $.confirm({
        type: "green",
        columnClass:"large",
        title: "ADD TAG",
        closeIcon: true,
        titleClass: "text-center",
        content: "url: " + $link.data("href"),
        onContentReady: function () {
            let self = this;
            $(document).on("submit",".add-tag-form",function(e){
                e.preventDefault();
                $form = $(this);
                var formdata = new FormData($(this)[0]);
                self.showLoading();
                $.ajax({
                    url: $form.attr("action"),
                    type: $form.attr("method"),
                    data: formdata,
                    processData: false,
                    contentType: false
                }).done(function(response){
                    self.hideLoading();
                    try {
                        let data = JSON.parse(response)[0];
                        if(data.status){
                            self.setContent(data.message);
                            self.setType("green");
                            self.$$save.hide();
                            setTimeout(function(){
                                self.close();
                            },2000)
                        }else{
                            self.setType("red");
                            self.setContent(data.message);
                            self.$$save.hide();
                        }
                    } catch (error) {
                        self.setType("red");
                        self.setContent(response)
                    }
                })

            });

        },
        buttons: {
            save: {
                text: "Save",
                btnClass: "btn-success",
                action: function(){
                    $(".add-tag-form").trigger("submit");
                    return false;
                }
            }
        },
        onOpenBefore: function(){
            $("body").css("overflow","hidden");
        },
        onClose: function(){
            window.location.reload();
        }
    });
});

$(document).on("click",".edit-tag-link",function(e){
    e.preventDefault();
    $link = $(this);
    $.confirm({
        type: "green",
        columnClass:"large",
        title: "EDIT TAG",
        closeIcon: true,
        titleClass: "text-center",
        content: "url: " + $link.data("href"),
        onContentReady: function () {
            let self = this;
            $(document).on("submit",".edit-tag-form",function(e){
                e.preventDefault();
                $form = $(this);
                var formdata = new FormData($(this)[0]);
                self.showLoading();
                $.ajax({
                    url: $form.attr("action"),
                    type: $form.attr("method"),
                    data: formdata,
                    processData: false,
                    contentType: false
                }).done(function(response){
                    self.hideLoading();
                    try {
                        let data = JSON.parse(response)[0];
                        if(data.status){
                            self.setContent(data.message);
                            self.setType("green");
                            self.$$save.hide();
                            setTimeout(function(){
                                self.close();
                            },2000)
                        }else{
                            self.setType("red");
                            self.setContent(data.message);
                            self.$$save.hide();
                        }
                    } catch (error) {
                        self.setType("red");
                        self.setContent(response)
                    }
                })

            });

        },
        buttons: {
            save: {
                text: "Save",
                btnClass: "btn-success",
                action: function(){
                    $(".edit-tag-form").trigger("submit");
                    return false;
                }
            }
        },
        onOpenBefore: function(){
            $("body").css("overflow","hidden");
        },
        onClose: function(){
            window.location.reload();
        }
    });
});


$(document).on("click", ".block-branch-link", function (e) {
    e.preventDefault();
    let $link = $(this);
    $.confirm({
        type: "red",
        title: "BLOCK BRANCH",
        titleClass: "text-center",
        columnClass: "medium",
        closeIcon: true,
        content: "Are you sure you want to block this from being used?",
        buttons: {
            cancel: {
                text: "no",
                btnClass: "btn-warning",
                action: function () {
                    var self = this;
                    self.close();
                    return false;
                }
            },
            confirm: {
                text: "yes",
                btnClass: "btn-warning",
                action: function () {
                    var self = this;
                    $.ajax({
                        url: $link.data("href"),
                        type: "GET",
                    }).done(function (response) {
                        try {
                            let data = JSON.parse(response)[0];
                            if (data.status) {
                                self.setType("green");
                                self.setContent(data.message);
                                self.$$cancel.hide();
                                self.$$confirm.hide();
                                setTimeout(function () {
                                    self.close();
                                }, 2000);
                            } else {
                                self.hideLoading();
                                self.setType("red");
                                self.setContent(data.message);
                            }
                        } catch (error) {
                            self.hideLoading();
                            self.setType("red");
                            self.setContent(response);
                        }
                    });
                    return false;
                }
            }
        },
        onOpenBefore: function () {
            $("body").css("overflow", "hidden");
        },
        onClose: function () {
            window.location.reload();
        }
    });
});

$(document).on("click", ".unblock-branch-link", function (e) {
    e.preventDefault();
    let $link = $(this);
    $.confirm({
        type: "red",
        title: "UNBLOCK BRANCH",
        titleClass: "text-center",
        columnClass: "medium",
        closeIcon: true,
        content: "Are you sure you want to unblock this?",
        buttons: {
            cancel: {
                text: "no",
                btnClass: "btn-warning",
                action: function () {
                    var self = this;
                    self.close();
                    return false;
                }
            },
            confirm: {
                text: "yes",
                btnClass: "btn-success",
                action: function () {
                    var self = this;
                    $.ajax({
                        url: $link.data("href"),
                        type: "GET",
                    }).done(function (response) {
                        try {
                            let data = JSON.parse(response)[0];
                            if (data.status) {
                                self.setType("green");
                                self.setContent(data.message);
                                self.$$cancel.hide();
                                self.$$confirm.hide();
                                setTimeout(function () {
                                    self.close();
                                }, 2000);
                            } else {
                                self.hideLoading();
                                self.setType("red");
                                self.setContent(data.message);
                            }
                        } catch (error) {
                            self.hideLoading();
                            self.setType("red");
                            self.setContent(response);
                        }
                    });
                    return false;
                }
            }
        },
        onOpenBefore: function () {
            $("body").css("overflow", "hidden");
        },
        onClose: function () {
            window.location.reload();
        }
    });
});

$(document).on("click", ".delete-branch-link", function (e) {
    e.preventDefault();
    let $link = $(this);
    $.confirm({
        type: "red",
        title: "DELETE BRANCH",
        titleClass: "text-center",
        columnClass: "medium",
        closeIcon: true,
        content: "Are you sure you want to delete this?",
        buttons: {
            cancel: {
                text: "no",
                btnClass: "btn-warning",
                action: function () {
                    var self = this;
                    self.close();
                    return false;
                }
            },
            confirm: {
                text: "yes",
                btnClass: "btn-warning",
                action: function () {
                    var self = this;
                    $.ajax({
                        url: $link.data("href"),
                        type: "GET",
                    }).done(function (response) {
                        try {
                            let data = JSON.parse(response)[0];
                            if (data.status) {
                                self.setType("green");
                                self.setContent(data.message);
                                self.$$cancel.hide();
                                self.$$confirm.hide();
                                setTimeout(function () {
                                    self.close();
                                }, 2000);
                            } else {
                                self.hideLoading();
                                self.setType("red");
                                self.setContent(data.message);
                            }
                        } catch (error) {
                            self.hideLoading();
                            self.setType("red");
                            self.setContent(response);
                        }
                    });
                    return false;
                }
            }
        },
        onOpenBefore: function () {
            $("body").css("overflow", "hidden");
        },
        onClose: function () {
            window.location.reload();
        }
    });
});