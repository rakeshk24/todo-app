// Run on the app's index page: coderabbit-agent-browser eval --stdin < tests/search_browser.js
(async () => {
    const input = document.getElementById('search-input');
    const container = document.getElementById('todos-container');
    const original = Array.from(container.childNodes);
    const realFetch = window.fetch;
    const realConfirm = window.confirm;
    const pending = [];
    const passed = [];
    const assert = (condition, message) => {
        if (!condition) throw new Error(message);
        passed.push(message);
    };
    const flush = () => new Promise(resolve => setTimeout(resolve, 0));
    const search = value => {
        input.value = value;
        input.dispatchEvent(new Event('input', {bubbles: true}));
    };
    const response = data => ({ok: true, json: async () => data});
    const todo = (title, fields = {}) => ({id: 12, title, completed: false, ...fields});
    window.fetch = url => new Promise((resolve, reject) => pending.push({url, resolve, reject}));
    try {
        assert(input.getAttribute('aria-label') === 'Search todos', 'accessible search label');
        assert(document.getElementById('search-limit').textContent.includes('50'), 'visible limit');
        search('%_');
        assert(pending[0].url.endsWith('q=%25_'), 'query is URL encoded');
        const payload = '<img src=x onerror="window.searchXss=true">';
        pending.shift().resolve(response([todo(payload, {
            description: payload, deadline: payload, completed: true, completed_at: payload
        })]));
        await flush();
        assert(container.querySelector('.todo-title').textContent === payload, 'literal title');
        assert(container.querySelector('.todo-description').textContent === payload,
            'literal description');
        assert(container.querySelector('.todo-deadline').textContent === 'Deadline: ' + payload,
            'literal deadline');
        assert(!container.querySelector('img') && !window.searchXss, 'no injected markup executes');
        assert(container.querySelector('.todo-item.completed input').checked, 'completed state');
        assert(container.querySelector('.todo-completed-at').textContent.includes(payload),
            'completion timestamp');
        assert(container.querySelector('.checkbox').getAttribute('href') === '/toggle/12',
            'toggle control');
        assert(container.querySelector('.btn-edit').getAttribute('href') === '/edit/12',
            'edit control');
        const remove = container.querySelector('.btn-delete');
        assert(remove.getAttribute('href') === '/delete/12', 'delete control');
        window.confirm = () => false;
        assert(!remove.dispatchEvent(new MouseEvent('click', {cancelable: true})),
            'delete confirmation can cancel');

        search('old');
        search('new');
        pending[1].resolve(response([todo('new')]));
        await flush();
        pending[0].resolve(response([todo('old')]));
        await flush();
        pending.splice(0);
        assert(container.querySelector('.todo-title').textContent === 'new', 'latest response wins');
        assert(!container.querySelector('.completed') && !container.querySelector('input').checked,
            'incomplete state');

        search('pending');
        search('');
        pending.shift().resolve(response([todo('obsolete')]));
        await flush();
        assert(original.every((node, i) => node === container.childNodes[i]),
            'clear restores original nodes and ignores late success');

        search('HTTP failure');
        pending.shift().resolve({ok: false, json: async () => []});
        await flush();
        assert(container.textContent.includes('Could not load'), 'HTTP error is visible');
        search('network failure');
        pending.shift().reject(new Error('offline'));
        await flush();
        assert(container.textContent.includes('Could not load'), 'network error is visible');
        search('late failure');
        search('current');
        pending[1].resolve(response([todo('current')]));
        await flush();
        pending[0].reject(new Error('old failure'));
        await flush();
        pending.splice(0);
        assert(container.querySelector('.todo-title').textContent === 'current',
            'stale failure cannot replace current results');
        search('cleared failure');
        search('');
        pending.shift().reject(new Error('cleared failure'));
        await flush();
        assert(original.every((node, i) => node === container.childNodes[i]),
            'clear ignores late failure');
        search('empty');
        pending.shift().resolve(response([]));
        await flush();
        assert(container.textContent.includes('No matching todos.'), 'empty state');
        return {passed: passed.length, checks: passed};
    } finally {
        window.fetch = realFetch;
        window.confirm = realConfirm;
        search('');
    }
})();
