import React, {useState, useEffect} from "react";
import "./CategoryList.css";
import {sendGet} from "../../utils.js";
import {url_categories, url_icons, url_icon} from "../../config.js";
import CategoryItem from "../CategoryItem/CategoryItem.jsx";
import IconList from "../iconList/iconList.jsx";
import Modal from "../modal/modal.jsx";

const CategoryList = (props) => {
    // const [categoryList, setCategoryList] = useState([])
    const [modalActive, setModalActive] = useState(false)
    const [iconList, setIconList] = useState([])
        
    // useEffect(() => sendGet(url_categories + props.group, (data) => {setCategoryList(data)}), [])
    
    function loadIcons () {
        if (iconList.length == 0) {
            sendGet(url_icons, (gettingIcons) => {setIconList(gettingIcons)})
        }
    }
    
    function createCategory () {
        const categoryNameInput = document.querySelector('.category-name-inp.' + props.group)
        const categoryIcon = document.querySelector('.cat-icon.active')
        // debugger
        props.categoryList.push({name: categoryNameInput.value, sum: '0', icon: categoryIcon.src.split('/').at(-1)})
        props.setCategoryList(props.categoryList)
    
        categoryNameInput.value = ""
        categoryIcon.className = 'cat-icon'
        setModalActive(false);
    }

    // function changeCategorySum (name, amount) {
    //     categoryList[name] = categoryList.sum - amount
    //     setCategoryList(categoryList)
    //     props.callback(to, amount)
    // }

    return (
        <div className={"categories " + props.group}>
            {props.categoryList.map(category => 
                <CategoryItem 
                    name={category.name} 
                    sum={category.sum}
                    catFrom={props.categoryFrom} 
                    setCatFrom={props.setCategoryFrom} 
                    setCatTo={props.setCategoryTo}
                    icon_url={url_icon + category.icon}
                    
                    clbAddOperation={props.clbAddOperation}
                    callback={props.callback}
                />
            )}        
            <button onClick={() => {loadIcons(); setModalActive(true)}}>add</button>
            
            <Modal active={modalActive} setActive={setModalActive}>
                <div>Название категории {props.group}</div>
                <input className={"category-name-inp " + props.group}/>
                <div>Выберите иконку:</div>
                <IconList iconList={iconList}/>
                <button onClick={createCategory}>create</button>
            </Modal>
        </div>
    )
};

export default CategoryList;