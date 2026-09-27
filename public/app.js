const form = document.getElementById('library-form');
const list = document.getElementById('library-list');
const emptyState = document.getElementById('empty-state');
const countBadge = document.getElementById('count-badge');

function showEmptyState(visible) {
  emptyState.classList.toggle('visible', visible);
}

function setCount(count) {
  countBadge.textContent = `${count} item${count === 1 ? '' : 's'}`;
}

function renderLibrary(items) {
  list.innerHTML = '';

  if (!items.length) {
    showEmptyState(true);
    setCount(0);
    return;
  }

  showEmptyState(false);
  setCount(items.length);

  items.forEach((item) => {
    const card = document.createElement('article');
    card.className = 'library-item';

    const actions = item.fileUrl
      ? `<a class="file-link" href="${item.fileUrl}" target="_blank" rel="noreferrer">Lihat file</a>`
      : '<span>Tidak ada file</span>';

    const html = `
      <div class="item-top">
        <div>
          <h3>${item.title}</h3>
          <span class="badge">${item.type}</span>
        </div>
        <button class="secondary-btn" data-id="${item.id}">Hapus</button>
      </div>
      <div class="meta">
        <span>Penulis: ${item.author}</span>
        <span>Tahun: ${item.year || '-'}</span>
      </div>
      <p class="description">${item.description || 'Tidak ada deskripsi.'}</p>
      <div class="item-actions">
        ${actions}
      </div>
    `;

    card.innerHTML = html;
    list.appendChild(card);
  });

  document.querySelectorAll('.secondary-btn').forEach((button) => {
    button.addEventListener('click', async () => {
      const { id } = button.dataset;
      await deleteItem(id);
    });
  });
}

async function loadLibrary() {
  try {
    const response = await fetch('/api/library');
    const items = await response.json();
    renderLibrary(items);
  } catch (error) {
    console.error('Gagal memuat library:', error);
    list.innerHTML = '<p class="description">Gagal memuat data.</p>';
  }
}

async function deleteItem(id) {
  try {
    const response = await fetch(`/api/library/${id}`, {
      method: 'DELETE'
    });

    if (!response.ok) {
      throw new Error('Gagal menghapus item');
    }

    await loadLibrary();
  } catch (error) {
    console.error(error);
    alert('Gagal menghapus data.');
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const formData = new FormData(form);

  try {
    const response = await fetch('/api/library', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Gagal menyimpan data');
    }

    form.reset();
    await loadLibrary();
  } catch (error) {
    console.error(error);
    alert(error.message || 'Gagal menyimpan data.');
  }
});

loadLibrary();
