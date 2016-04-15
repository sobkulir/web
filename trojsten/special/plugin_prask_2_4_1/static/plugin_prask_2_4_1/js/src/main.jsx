var Question = React.createClass({
    render: function () {
        return <li><span className="label label-info">{this.props.a} > {this.props.b}</span>&nbsp;
            Zlúčenina <em>č. {this.props.a}</em> je väčšia ako zlúčenina <em>č. {this.props.b}</em>.
        </li>;
    }
});

var QuestionList = React.createClass({
    url: '/specialne/prask/2/4/1/api/query/',
    getInitialState: function () {
        return {
            form_a: '',
            form_b: '',
            questions: []
        }
    },
    componentDidMount: function () {
        $.getJSON(this.url, function (data) {
            if (data.status == 'Success') {
                this.setState({questions: data.queries});
            }
        }.bind(this));
    },
    handleReset: function () {
        $.ajax({
            url: this.url,
            type: 'DELETE',
            dataType: 'json',
            success: function (data) {
                if (data.status == 'Success') {
                    this.setState({questions: data.queries});
                }
            }.bind(this)
        });
    },
    handleFormAChange: function (event) {
        var new_a = event.target.value;
        this.setState({form_a: new_a});
    },
    handleFormBChange: function (event) {
        var new_b = event.target.value;
        this.setState({form_b: new_b});
    },
    handleSubmit: function (event) {
        $.post(
            this.url,
            {a: this.state.form_a, b: this.state.form_b},
            function (data) {
                if (data.status == 'Success') {
                    this.setState({questions: data.queries});
                } else {
                    alert(data.message);
                }
            }.bind(this), 'json');
        return true;
    },
    render: function () {
        var questions = this.state.questions.map(function (item, index) {
            return <Question key={index} a={item[0]} b={item[1]}/>;
        });
        return <div>
            Odpovede na tvoje doterajšie otázky:
            <ol>{questions}</ol>
            <form className="form form-inline">
                <label>Porovnaj:</label>
                <input type="number" value={this.state.form_a} onChange={this.handleFormAChange}
                       className="form-control"/>
                &nbsp;a&nbsp;
                <input type="number" value={this.state.form_b} onChange={this.handleFormBChange}
                       className="form-control"/>
                <button type="button" className="btn btn-primary" onClick={this.handleSubmit}>Porovnaj</button>
                <button type="button" className="btn btn-danger" onClick={this.handleReset}>Reset</button>
            </form>
        </div>;
    }
});

ReactDOM.render(
    <QuestionList />, document.getElementById("plugin_prask_2_4_1/questions")
);
