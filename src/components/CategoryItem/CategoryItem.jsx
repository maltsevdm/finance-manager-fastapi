import React from "react";
import './CategoryItem.css';

const CategoryItem = (props) => {

    function dragStartHandler(e, name) {
        
        props.setCatFrom(name)
        // debugger
    };
    
    function dragLeaveHandler(e) {
        // console.log(e)
    };
    
    function dragEndHandler(e) {
    
        // console.log(e)
    };
    
    function dragOverHandler(e) {
        e.preventDefault()
    
        // console.log(e)
    };
    
    function dragDropHandler(e, name) {
        e.preventDefault()
        props.setCatTo(name)
        // props.setOperModalActive(true)

        props.callback(props.catFrom, name)


        // if (catFrom === name) {
        //     return;
        // };
        
        // let data = {
        //     type: "expense",
        //     category: "product",
        //     amount: 500
        // }
        
        // console.log(catFrom, '=>', name)

        // sendPost('http://127.0.0.1:8000/operation', data, console.log)
        // sendGet('http://127.0.0.1:8000/operation', console.log)    
    };
    
    return (
        <div className="cat-item">
            <div>{props.name}</div>
            <img 
                key={props.name}
                draggable={true}
                onDragStart={(e) => dragStartHandler(e, props.name)}
                onDragLeave={(e) => dragLeaveHandler(e)}
                onDragEnd={(e) => dragEndHandler(e)}
                onDragOver={(e) => dragOverHandler(e)}
                onDrop={(e) => dragDropHandler(e, props.name)}
                src={props.icon_url}
                onClick={ () => {console.log('Hello')}}/>
            <div>{props.sum}</div>
        </div>
    )
};

export default CategoryItem;