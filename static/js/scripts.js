function excluirProfessor(id_professor) {
    if (confirm("Tem certeza que deseja excluir este professor?")) {
        fetch(`/exclusao-professor/${id_professor}`, { method: "POST" })
            .then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert("Erro ao excluir professor!");
                }
            })
            .catch(error => alert("Erro na requisição: " + error));
    }
}
