async function loadContent(endpoint) {
    showOverlay()
    const res = await fetch(endpoint);
    const data = await res.text();
    document.getElementById("content").innerHTML = data;
    hideOverlay()
}

function createBook() {
    $("#createBookModal").modal('show');
}

async function onSaveBook() {
    let bookTitle = $("[name='book_title']").val();
    let bookPrice = $("[name='book_price']").val() || 0;
    let bookData = {
        'title': bookTitle,
        'price': bookPrice
    }
    if (bookTitle == '') {
        alert("Please Input Title")
    } else {
        const res = await fetch(`/api/books`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                title: bookTitle,
                price: bookPrice,
                availability: "In stock",
                product_link: "",
                rating: 5,
                publisher_country: "0"
            })
        });
        $("#createBookModal").modal('hide');
        const data = await res.text();
        document.getElementById("content").innerHTML = data;
        alert('Create Book Success')
    }
}

async function searchBookWithCountry() {
    showOverlay()
    var value = document.getElementById("search_book_value").value
    const res = await fetch(`/api/books?country=${value}`);
    const data = await res.text();
    document.getElementById("content").innerHTML = data;
    hideOverlay()
}

async function deleteBook(event){
    if (!confirm('Are you sure you want to delete this book?')) return;
    const button = event.currentTarget;
    const row = button.closest("tr");
    const title = row.querySelector('.book-title').textContent.trim();
    const res = await fetch(`/api/books/${encodeURIComponent(title)}`, {
        method: "DELETE"
    });
    $(row).remove();
}

function showOverlay() {
    document.getElementById("overlay").classList.remove("d-none");
}

function hideOverlay() {
    document.getElementById("overlay").classList.add('d-none');
}
